import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def buscar_planta(nome):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT umidade_min, umidade_max, temperatura_min, temperatura_max
        FROM plantas
        WHERE nome = %s
    """, (nome.lower(),))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return None
    return {
        "umidade_min": row[0],
        "umidade_max": row[1],
        "temperatura_min": row[2],
        "temperatura_max": row[3]
    }

def calcular_saude_umidade(umidade, minimo, maximo):
    if minimo <= umidade <= maximo:
        return 100
    if umidade < minimo:
        diferenca = minimo - umidade
        return max(0, 100 - diferenca * 2)
    diferenca = umidade - maximo
    return max(0, 100 - diferenca * 2)

def calcular_saude_temperatura(temperatura, minimo, maximo):
    if minimo <= temperatura <= maximo:
        return 100
    if temperatura < minimo:
        diferenca = minimo - temperatura
        return max(0, 100 - diferenca * 5)
    diferenca = temperatura - maximo
    return max(0, 100 - diferenca * 5)

def analisar_planta(planta, umidade, temperatura):
    planta = planta.lower()

    dados = buscar_planta(planta)

    if not dados:
        return 0, ["Planta não cadastrada"]

    recomendacoes = []

    saude_umidade = calcular_saude_umidade(
        umidade,
        dados["umidade_min"],
        dados["umidade_max"]
    )

    saude_temperatura = calcular_saude_temperatura(
        temperatura,
        dados["temperatura_min"],
        dados["temperatura_max"]
    )

    saude = int((saude_umidade + saude_temperatura) / 2)

    if umidade < dados["umidade_min"]:
        recomendacoes.append("Solo seco → irrigar")
    elif umidade > dados["umidade_max"]:
        recomendacoes.append("Solo encharcado → reduzir irrigação")

    if temperatura < dados["temperatura_min"]:
        recomendacoes.append("Temperatura baixa → proteger planta")
    elif temperatura > dados["temperatura_max"]:
        recomendacoes.append("Temperatura alta → reduzir exposição ao calor")

    if len(recomendacoes) == 0:
        recomendacoes.append("Condições ideais")

    return saude, recomendacoes