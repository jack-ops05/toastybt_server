import os
from collections.abc import Iterator
from datetime import datetime

import pandas as pd
from fastapi import HTTPException

def handler(symbol: str, start: str, end: str):

    symbol_dir = os.path.join(
        "market_data",
        symbol,
        "1m"
    )

    if not os.path.exists(symbol_dir):
        raise HTTPException(
            status_code=404,
            detail=f"Symbol {symbol} not found request /get_metadata for available symbols"
        )

    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Start and end dates must be ISO format tz-aware -> [ 2012-01-01T00:00:00+00:00 ]"
        )

    if start_dt >= end_dt:
        raise HTTPException(
            status_code=400,
            detail="Start date must be before end date"
        )

    return stream_data(symbol_dir, start_dt, end_dt)

#Generator function
def stream_data(symbol_dir: str, start_dt: datetime, end_dt: datetime) -> Iterator[str]:

    current_year = start_dt.year
    current_month = start_dt.month

    end_year = end_dt.year
    end_month = end_dt.month

    while (current_year < end_year or (current_year == end_year and current_month <= end_month)):

        file_path = os.path.join(
            symbol_dir,
            str(current_year),
            f"{current_year}-{current_month:02d}.parquet"
        )
    
        if os.path.exists(file_path):
    
            df = pd.read_parquet(file_path)
    
            df = df[(df["timestamp"] >= start_dt) & (df["timestamp"] < end_dt)]
    
            if not df.empty:
    
                json_data = df.to_json(orient="records", lines=True, date_format="iso")
    
                if isinstance(json_data, str):
                    yield json_data

        current_month += 1
    
        if current_month == 13:
            current_month = 1
            current_year += 1