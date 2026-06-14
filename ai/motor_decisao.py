import os
import json
import psycopg2
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

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

def buscar_planta_groq(nome):
    prompt = f"""Você é um agrônomo especialista em cultivo de plantas tropicais e hortaliças.
Retorne APENAS um JSON válido com os parâmetros ideais de cultivo para a planta "{nome}".
O JSON deve ter exatamente este formato, sem texto adicional:
{{
    "umidade_min": <número inteiro entre 0 e 100>,
    "umidade_max": <número inteiro entre 0 e 100>,
    "temperatura_min": <número inteiro em graus Celsius>,
    "temperatura_max": <número inteiro em graus Celsius>
}}
Use valores agronomicamente corretos baseados em literatura científica."""

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=200
        )
        texto = response.choices[0].message.content.strip()
        dados = json.loads(texto)
        salvar_planta_banco(nome, dados)
        return dados
    except Exception as e:
        print(f"Erro ao buscar planta no Groq: {e}")
        return None

def salvar_planta_banco(nome, dados):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO plantas (nome, umidade_min, umidade_max, temperatura_min, temperatura_max, luz)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (nome) DO NOTHING
        """, (
            nome.lower(),
            dados["umidade_min"],
            dados["umidade_max"],
            dados["temperatura_min"],
            dados["temperatura_max"],
            "media"
        ))
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ Planta '{nome}' salva no banco via Groq")
    except Exception as e:
        print(f"Erro ao salvar planta no banco: {e}")

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
        print(f"Planta '{planta}' não encontrada no banco. Consultando Groq...")
        dados = buscar_planta_groq(planta)

    if not dados:
        return 0, ["Planta não cadastrada e não foi possível obter parâmetros"]

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