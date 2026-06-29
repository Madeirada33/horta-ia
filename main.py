# uvicorn main:app --reload
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from models.dados import DadosHorta
from ai.motor_decisao import analisar_planta
from ai.tendencia import analisar_tendencia
from storage.historico import salvar_dados, carregar_dados
from bot import enviar_alerta
from auth import criar_token
import banco_usuario
import os
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="."), name="static")

# =======================================================
# MODELOS DE DADOS (Pydantic)
# =======================================================

class UsuarioCadastro(BaseModel):
    nome: str
    email: str
    senha: str

class UsuarioLogin(BaseModel):
    email: str
    senha: str

# =======================================================
# ROTAS DA API
# =======================================================

@app.get("/", response_class=HTMLResponse)
def dashboard():
    caminho = os.path.join(os.path.dirname(__file__), "dashboard.html")
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/usuarios/cadastro", status_code=201)
def cadastrar_novo_usuario(usuario: UsuarioCadastro):
    novo_id = banco_usuario.criar_usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_plana=usuario.senha
    )
    if not novo_id:
        raise HTTPException(
            status_code=400,
            detail="Não foi possível realizar o cadastro. E-mail já existente ou dados inválidos."
        )
    return {
        "status": "sucesso",
        "mensagem": "Usuário criado com sucesso!",
        "usuario_id": novo_id
    }

@app.post("/usuarios/login")
def login(usuario: UsuarioLogin):
    dados = banco_usuario.login_usuario(
        email=usuario.email,
        senha_plana=usuario.senha
    )
    if not dados:
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha incorretos."
        )
    token = criar_token(
        usuario_id=dados["id"],
        nome=dados["nome"],
        email=dados["email"]
    )
    return {
        "status": "sucesso",
        "token": token,
        "usuario": {
            "id": dados["id"],
            "nome": dados["nome"],
            "email": dados["email"]
        }
    }

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