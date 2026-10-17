import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import databento as db

url = "http://127.0.0.1:8000/download_data"

body = {
    "server_symbol": "ES",
    "dataset": "GLBX.MDP3",
    "start": "2026-10-08T00:00:00+00:00",
    "end": "2026-10-13T00:00:00+00:00",
    "databento_symbol": "ES.v.0",
    "db_schema": "ohl-1m"
}

body2 = {
    "symbol": "NQ",
    "start": "2026-10-08T00:00:00+00:00",
    "end": "2026-10-17T00:00:00+00:00"
}

res = requests.post(url, json=body)
print(res.text)
