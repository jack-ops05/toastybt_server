import json
import logging
import os
from datetime import UTC, datetime, timedelta

import databento as db
import pandas as pd

from misc.alerts import send_alert

logger = logging.getLogger("sync")

def sync_symbols():

    client = db.Historical(os.getenv("DATABENTO_API_KEY"))
    
    #Iterate for each symbol
    for symbol in os.listdir("./market_data"):

        base_dir = os.path.join(
            "market_data",
            symbol,
            "1m"
        )
        metadata_path = os.path.join(
            base_dir,
            "metadata.json"
        )
        
        if not os.path.exists(metadata_path):
            logger.error(f"Failed to sync {symbol} could not find metadata")
            send_alert(f"Failed to sync {symbol}, could not find metadata")
            continue

        #Load metadata
        with open(metadata_path, "r") as file:
            metadata = json.load(file)

        #Extract metadata
        databento_symbol = metadata["databento_symbol"]
        dataset = metadata["dataset"]
        schema = metadata["schema"]
        start = datetime.fromisoformat(metadata["max_timestamp"]) + timedelta(minutes=1)
        end = datetime.now(UTC)

        #Download data
        try:
            data = client.timeseries.get_range(
                dataset=dataset,
                start=start,
                end=end,
                symbols=databento_symbol,
                schema=schema,
                stype_in="continuous"
            )
        except Exception:
            logger.exception(f"Failed to sync {symbol} Databento API error")
            send_alert(f"Failed to sync {symbol}, Databento API error")
            continue

        #Reframe new data
        new_df = data.to_df()

        if new_df.empty:
            continue

        new_df = new_df.reset_index()
        new_df = new_df.drop(columns=["rtype", "publisher_id", "instrument_id", "symbol"])
        new_df = new_df.rename(columns={"ts_event": "timestamp"})
        new_df = new_df.sort_values("timestamp")

        #Group data by year/month
        new_df["year"] = new_df["timestamp"].dt.year
        new_df["month"] = new_df["timestamp"].dt.month
        grouped = new_df.groupby(["year", "month"])

        rows_added = 0

        #Iterate each group
        for key, monthly_df in grouped:
            year = key[0]
            month = key[1]

            year_dir = os.path.join(
                base_dir,
                str(year)
            )
            os.makedirs(year_dir, exist_ok=True)

            file_path = os.path.join(year_dir, f"{year}-{month:02d}.parquet")
            monthly_df = monthly_df.drop(columns=["year", "month"])

            #Update if monthly parquet exists
            if os.path.exists(file_path):
                current_df = pd.read_parquet(file_path)
                old_row_count = len(current_df)
                combined_df = pd.concat([current_df, monthly_df], ignore_index=True)
                combined_df = (combined_df.drop_duplicates(subset=["timestamp"], keep="last").sort_values("timestamp"))
                combined_df.to_parquet(file_path, index=False)
                rows_added += len(combined_df) - old_row_count

            #Create if monthly parquet doesn't exist
            else:
                monthly_df = (monthly_df.drop_duplicates(subset=["timestamp"], keep="last").sort_values("timestamp"))
                monthly_df.to_parquet(file_path, index=False)
                rows_added += len(monthly_df)

        #Update metadata
        metadata["max_timestamp"] = (new_df["timestamp"].max().isoformat())
        metadata["row_count"] += rows_added
        metadata["last_sync"] = (datetime.now(UTC).isoformat())

        with open(metadata_path, "w") as file:
            json.dump(metadata, file, indent=4)

        logger.info(f"Sync complete for {symbol}, {rows_added} rows added")

    send_alert("Daily data sync complete")