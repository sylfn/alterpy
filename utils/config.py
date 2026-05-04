import json
import os

def load(name: str) -> dict:
    with open(f"./config/{name}.json", "r+") as f:
        return json.load(f)

