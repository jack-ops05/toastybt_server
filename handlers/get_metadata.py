import json
import os

def handler():

    full_metadata = {}

    #Find each available symbols metadata
    for symbol in os.listdir("./market_data"):

        metadata_file = os.path.join(
            "market_data",
            symbol,
            "1m",
            "metadata.json"
        )

        if not os.path.exists(metadata_file):
            continue

        with open(metadata_file, "r") as file:
            metadata = json.load(file)

        full_metadata[symbol] = metadata

    return full_metadata