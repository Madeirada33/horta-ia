import json

with open("data/plantas.json", "r", encoding="utf-8") as arquivo:
    plantas = json.load(arquivo)