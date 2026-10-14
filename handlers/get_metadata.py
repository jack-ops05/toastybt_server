import json
import logging
import os

logger = logging.getLogger("handlers")

def handler():

    full_metadata = {}
    for symbol in os.listdir("./market_data"):

        metadata_file = os.path.join(
            "market_data",
            symbol,
            "1m",
            "metadata.json"
        )

        if not os.path.exists(metadata_file):
            logger.warning(f"Symbol {symbol} is missing metadata")
            continue

        with open(metadata_file, "r") as file:
            metadata = json.load(file)

        full_metadata[symbol] = metadata

    return full_metadata