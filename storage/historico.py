import json
from datetime import datetime

ARQUIVO = "storage/dados_horta.json"

def salvar_dados(planta, umidade, temperatura, saude):

    registro = {
        "planta": planta,
        "umidade": umidade,
        "temperatura": temperatura,
        "saude": saude,
        "data": datetime.now().isoformat()
    }

    try:
        with open(ARQUIVO, "r") as f:
            dados = json.load(f)
    except:
        dados = []

    dados.append(registro)

    with open(ARQUIVO, "w") as f:
        json.dump(dados, f, indent=4)