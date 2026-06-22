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
    prompt = f"""Você é um agrônomo especialista em cultivo de plantas no geral.
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

def analisar_planta(planta, umidade_solo, temperatura_solo, dados_previsao=None):
    planta = planta.lower()
    dados = buscar_planta(planta)

    if not dados:
        print(f"Planta '{planta}' não encontrada... Consultando Groq...")
        dados = buscar_planta_groq(planta)

    if not dados:
        return 0, ["Planta não cadastrada e sem parâmetros disponíveis"]

    recomendacoes = []

    saude_umidade = calcular_saude_umidade(umidade_solo, dados["umidade_min"], dados["umidade_max"])
    saude_temperatura = calcular_saude_temperatura(temperatura_solo, dados["temperatura_min"], dados["temperatura_max"])
    saude = int((saude_umidade + saude_temperatura) / 2)

    # 1. PREDITIVIDADE DE UMIDADE (Solo vs Chuva do Futuro)
    if umidade_solo < dados["umidade_min"]:
        if dados_previsao and dados_previsao["vai_chover_logo"]:
            recomendacoes.append(
                f"Solo seco ({umidade_solo}%), mas há previsão de chuva para as próximas horas ({dados_previsao['descricao_futura']}). Irrigação suspensa preventivamente."
            )
        else:
            recomendacoes.append("Solo seco → irrigar")
            
    elif umidade_solo > dados["umidade_max"]:
        recomendacoes.append("Solo encharcado → suspender irrigações")

    # 2. PREDITIVIDADE DE TEMPERATURA (Calor vindo por aí)
    if temperatura_solo > dados["temperatura_max"]:
        recomendacoes.append("Temperatura alta no solo → reduzir exposição ao calor")
    elif dados_previsao and dados_previsao["temperatura_ar_futura"] > dados["temperatura_max"]:
        # O solo ainda não esquentou, mas o ar das próximas horas vai passar do limite da planta
        recomendacoes.append(
            f"Alerta: Previsão de calor excessivo ({int(dados_previsao['temperatura_ar_futura'])}°C) nas próximas horas. Considere mover a planta para a sombra antes que o solo superaqueça."
        )

    if len(recomendacoes) == 0:
        recomendacoes.append("Condições ideais")

    return saude, recomendacoes