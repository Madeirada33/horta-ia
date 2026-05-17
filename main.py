# uvicorn main:app --reload
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from models.dados import DadosHorta
from ai.motor_decisao import analisar_planta
from storage.historico import salvar_dados, carregar_dados
from bot import enviar_alerta
import os
 
app = FastAPI()
 
@app.get("/", response_class=HTMLResponse)
def dashboard():
    caminho = os.path.join(os.path.dirname(__file__), "dashboard.html")
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()
 
@app.post("/dados-horta")
def receber_dados(dados: DadosHorta):
 
    saude, recomendacoes = analisar_planta(
        dados.planta,
        dados.umidade_solo,
        dados.temperatura
    )
 
    salvar_dados(
        dados.planta,
        dados.umidade_solo,
        dados.temperatura,
        saude
    )
 
    enviar_alerta(
        dados.planta,
        dados.umidade_solo,
        dados.temperatura,
        saude,
        recomendacoes
    )
 
    return {
        "planta": dados.planta,
        "saude": saude,
        "recomendacoes": recomendacoes
    }
 
@app.get("/historico")
def historico():
    return carregar_dados()
 
@app.get("/ultimo-dado")
def ultimo_dado():
    dados = carregar_dados()
    if not dados:
        return {}
    ultimo = dados[-1]
    saude, recomendacoes = analisar_planta(
        ultimo["planta"],
        ultimo["umidade"],
        ultimo["temperatura"]
    )
    ultimo["recomendacoes"] = recomendacoes
    return ultimo