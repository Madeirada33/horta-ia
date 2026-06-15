import os
import psycopg2
from dotenv import load_dotenv

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
    return [{"umidade": r[0], "temperatura": r[1], "data": r[2]} for r in rows]

def buscar_parametros_planta(planta):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT umidade_min, umidade_max, temperatura_min, temperatura_max
        FROM plantas
        WHERE nome = %s
    """, (planta.lower(),))
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

def calcular_taxa_variacao(valores, intervalo_minutos=30):
    """
    Calcula a taxa de variação por hora baseada nos registros.
    Retorna variação por hora.
    """
    if len(valores) < 2:
        return 0

    # Pega o primeiro e último valor
    variacao_total = valores[-1] - valores[0]
    horas_totais = (len(valores) - 1) * (intervalo_minutos / 60)

    if horas_totais == 0:
        return 0

    return variacao_total / horas_totais

def projetar_horas(valor_atual, limite, taxa_por_hora):
    """
    Projeta em quantas horas o valor vai atingir o limite.
    Retorna None se não vai atingir.
    """
    if taxa_por_hora == 0:
        return None

    distancia = limite - valor_atual
    horas = distancia / taxa_por_hora

    if horas <= 0:
        return None

    return round(horas, 1)

def formatar_tempo(horas):
    if horas < 1:
        minutos = int(horas * 60)
        return f"{minutos} minutos"
    elif horas < 2:
        return "aproximadamente 1 hora"
    else:
        return f"aproximadamente {int(horas)} horas"

def analisar_tendencia(planta):
    """
    Analisa tendência e projeta quando parâmetros vão atingir limites críticos.
    Retorna alertas em linguagem simples e prática.
    """
    historico = buscar_historico_recente(planta, horas=6)
    parametros = buscar_parametros_planta(planta)

    if len(historico) < 3 or not parametros:
        return []

    umidades = [r["umidade"] for r in historico]
    temperaturas = [r["temperatura"] for r in historico]

    taxa_umidade = calcular_taxa_variacao(umidades)
    taxa_temperatura = calcular_taxa_variacao(temperaturas)

    umidade_atual = umidades[-1]
    temperatura_atual = temperaturas[-1]

    alertas = []

    # Análise de umidade
    if taxa_umidade < -2:  # secando mais de 2% por hora
        horas_ate_seco = projetar_horas(
            umidade_atual,
            parametros["umidade_min"],
            taxa_umidade
        )
        if horas_ate_seco and horas_ate_seco <= 12:
            tempo = formatar_tempo(horas_ate_seco)
            alertas.append(
                f"🌵 Solo secando rapidamente. Sem irrigação, a planta entrará em estresse em {tempo}."
            )

    elif taxa_umidade > 2:  # encharcando mais de 2% por hora
        horas_ate_encharcado = projetar_horas(
            umidade_atual,
            parametros["umidade_max"],
            taxa_umidade
        )
        if horas_ate_encharcado and horas_ate_encharcado <= 12:
            tempo = formatar_tempo(horas_ate_encharcado)
            alertas.append(
                f"💧 Solo encharcando rapidamente. O excesso de água pode prejudicar a planta em {tempo}."
            )

    # Análise de temperatura
    if taxa_temperatura > 1:  # aquecendo mais de 1°C por hora
        horas_ate_quente = projetar_horas(
            temperatura_atual,
            parametros["temperatura_max"],
            taxa_temperatura
        )
        if horas_ate_quente and horas_ate_quente <= 12:
            tempo = formatar_tempo(horas_ate_quente)
            alertas.append(
                f"🔥 Temperatura subindo. A planta pode sofrer com o calor em {tempo}. Considere sombreamento."
            )

    elif taxa_temperatura < -1:  # esfriando mais de 1°C por hora
        horas_ate_frio = projetar_horas(
            temperatura_atual,
            parametros["temperatura_min"],
            taxa_temperatura
        )
        if horas_ate_frio and horas_ate_frio <= 12:
            tempo = formatar_tempo(horas_ate_frio)
            alertas.append(
                f"🥶 Temperatura caindo. A planta pode sofrer com o frio em {tempo}. Considere proteção."
            )

    return alertas