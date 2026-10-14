import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI

from routing import routes

load_dotenv()

os.makedirs("market_data", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(asctime)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

app = FastAPI()
app.include_router(routes.router)