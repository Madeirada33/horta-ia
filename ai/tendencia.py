import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def buscar_historico_recente(planta, horas=6):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT umidade, temperatura, data
        FROM historico
        WHERE planta = %s
          AND data >= NOW() - INTERVAL '%s hours'
        ORDER BY data ASC
    """, (planta.lower(), horas))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "umidade": r[0],
            "temperatura": r[1],
            "data": r[2]
        }
        for r in rows
    ]

def calcular_tendencia(valores):
    """
    Recebe uma lista de valores numéricos e retorna:
    - "subindo" se há tendência de alta
    - "descendo" se há tendência de queda
    - "estavel" se não há tendência clara
    """
    if len(valores) < 3:
        return "estavel", 0

    primeiro = sum(valores[:3]) / 3
    ultimo = sum(valores[-3:]) / 3
    variacao = ultimo - primeiro

    if variacao <= -5:
        return "descendo", round(variacao, 1)
    elif variacao >= 5:
        return "subindo", round(variacao, 1)
    else:
        return "estavel", round(variacao, 1)

def analisar_tendencia(planta):
    """
    Analisa a tendência de umidade e temperatura das últimas 6 horas.
    Retorna lista de alertas de tendência.
    """
    historico = buscar_historico_recente(planta, horas=6)

    if len(historico) < 3:
        return []

    umidades = [r["umidade"] for r in historico]
    temperaturas = [r["temperatura"] for r in historico]

    tendencia_umidade, variacao_umidade = calcular_tendencia(umidades)
    tendencia_temperatura, variacao_temperatura = calcular_tendencia(temperaturas)

    alertas = []

    # Alertas de umidade
    if tendencia_umidade == "descendo":
        alertas.append(
            f"⚠️ Tendência de secagem: umidade caiu {abs(variacao_umidade):.1f}% nas últimas 6 horas"
        )
    elif tendencia_umidade == "subindo":
        alertas.append(
            f"⚠️ Tendência de encharcamento: umidade subiu {variacao_umidade:.1f}% nas últimas 6 horas"
        )

    # Alertas de temperatura
    if tendencia_temperatura == "subindo":
        alertas.append(
            f"⚠️ Tendência de aquecimento: temperatura subiu {variacao_temperatura:.1f}°C nas últimas 6 horas"
        )
    elif tendencia_temperatura == "descendo":
        alertas.append(
            f"⚠️ Tendência de resfriamento: temperatura caiu {abs(variacao_temperatura):.1f}°C nas últimas 6 horas"
        )

    return alertas