import json
import logging
import os
from datetime import UTC, datetime

import databento as db
from fastapi import HTTPException

logger = logging.getLogger("handlers")

def handler(dataset: str, start: str, end: str, databento_symbol: str, schema: str, server_symbol: str):

    symbol_dir = os.path.join(
        "market_data",
        server_symbol,
        "1m"
    )

    #Request data
    try:
        client = db.Historical(os.getenv("DATABENTO_API_KEY"))
        data = client.timeseries.get_range(
            dataset=dataset,
            start=start,
            end=end,
            symbols=databento_symbol,
            schema=schema,
            stype_in="continuous"
        )
    except Exception:
        logger.exception("Databento API request error")
        raise HTTPException(
            status_code=502,
            detail="Databento API request error check logs for details"
        )

    #Clean data
    df = data.to_df()
    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Databento returned empty data for symbol {server_symbol}"
        )

    df = df.reset_index()
    df = df.drop(columns=["rtype", "publisher_id", "instrument_id", "symbol"])
    df = df.rename(columns={"ts_event": "timestamp"})
    df = df.sort_values("timestamp")

    #Group data by year/month
    df["year"] = df["timestamp"].dt.year
    df["month"] = df["timestamp"].dt.month
    grouped = df.groupby(["year", "month"])

    #Iterate each group
    for key, monthly_df in grouped:
        year = key[0]
        month = key[1]
        year_dir = os.path.join(
            symbol_dir,
            str(year)
        )

        #Save parquet file
        os.makedirs(year_dir, exist_ok=True)
        file_path = os.path.join(year_dir, f"{year}-{month:02d}.parquet")
        monthly_df = monthly_df.drop(columns=["year", "month"])
        monthly_df.to_parquet(file_path, index=False)

    #Initialize metadata
    metadata = {
        "symbol": server_symbol,
        "databento_symbol": databento_symbol,
        "dataset": dataset,
        "schema": schema,
        "data_type": "continuous",
        "min_timestamp": df["timestamp"].min().isoformat(),
        "max_timestamp": df["timestamp"].max().isoformat(),
        "row_count": len(df),
        "last_sync": datetime.now(UTC).isoformat(),
    }

    metadata_path = os.path.join(
        symbol_dir,
        "metadata.json"
    )
    with open(metadata_path, "w") as file:
        json.dump(metadata, file, indent=4)

    logger.info(f"Successfully downloaded {metadata["schema"]} data for symbol {server_symbol} from [ {metadata["min_timestamp"]} ] -> [ {metadata["max_timestamp"]} ]")