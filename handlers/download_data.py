import json
import os
from datetime import UTC, datetime

import databento as db
from databento import BentoClientError, BentoServerError
from fastapi import HTTPException


def handler(server_symbol: str, dataset: str, start: str, end: str, databento_symbol: str, schema: str):

    #Check if symbol already exists
    for symbol in os.listdir("./market_data"):
        if symbol == server_symbol:
            raise HTTPException(
                status_code=400,
                detail="Symbol already exist in the server"
            )

    #Download data
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
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except (BentoClientError, BentoServerError) as e:
        raise HTTPException(
            status_code=e.http_status,
            detail=e.message
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

    symbol_dir = os.path.join(
        "market_data",
        server_symbol,
        "1m"
    )

    #Iterate each group
    try:
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
    except Exception as e:
        df.to_parquet(f"failed_save_{server_symbol}", index=False)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )