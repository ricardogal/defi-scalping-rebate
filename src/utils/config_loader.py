import json
from pathlib import Path

def carregar_config():
    caminho = Path(__file__).parent.parent.parent / "config.json"
    with open(caminho, "r") as f:
        return json.load(f)
