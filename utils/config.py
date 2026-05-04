import pytomlpp
import os

def load(name: str) -> dict:
    path = f"./config/{name}.toml"
    if not os.path.exists(path):
        with open(path, "w") as f:
            pass
    return pytomlpp.load(path)

