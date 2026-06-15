# uvicorn main:app --reload
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from models.dados import DadosHorta
from ai.motor_decisao import analisar_planta
from ai.tendencia import analisar_tendencia
from storage.historico import salvar_dados, carregar_dados
from bot import enviar_alerta
import os
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="."), name="static")

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

    # Analisa tendência e adiciona alertas às recomendações
    alertas_tendencia = analisar_tendencia(dados.planta)
    recomendacoes_completas = recomendacoes + alertas_tendencia

    enviar_alerta(
        dados.planta,
        dados.umidade_solo,
        dados.temperatura,
        saude,
        recomendacoes_completas
    )

    return {
        "planta": dados.planta,
        "saude": saude,
        "recomendacoes": recomendacoes_completas
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
    alertas_tendencia = analisar_tendencia(ultimo["planta"])
    ultimo["recomendacoes"] = recomendacoes + alertas_tendencia
    return ultimo