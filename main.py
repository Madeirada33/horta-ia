# uvicorn main:app --reload
from fastapi import FastAPI
from models.dados import DadosHorta
from ai.motor_decisao import analisar_planta
from storage.historico import salvar_dados
from bot import enviar_alerta
 
app = FastAPI()
 
@app.get("/")
def home():
    return {"mensagem": "Servidor da horta inteligente"}
 
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
 