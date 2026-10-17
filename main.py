import os

from dotenv import load_dotenv
from fastapi import FastAPI

from routing import routes

load_dotenv()

os.makedirs("market_data", exist_ok=True)

app = FastAPI()
app.include_router(routes.router)