import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_PUBLIC_URL")

plantas = {
    # Hortaliças
    "alface": {
        "umidade_min": 40, "umidade_max": 80,
        "temperatura_min": 10, "temperatura_max": 25,
        "luz": "media"
    },
    "tomate": {
        "umidade_min": 60, "umidade_max": 80,
        "temperatura_min": 10, "temperatura_max": 25,
        "luz": "alta"
    },
    "cenoura": {
        "umidade_min": 35, "umidade_max": 80,
        "temperatura_min": 10, "temperatura_max": 24,
        "luz": "media"
    },
    "couve": {
        "umidade_min": 45, "umidade_max": 70,
        "temperatura_min": 12, "temperatura_max": 26,
        "luz": "media"
    },
    "cebola": {
        "umidade_min": 30, "umidade_max": 80,
        "temperatura_min": 13, "temperatura_max": 28,
        "luz": "alta"
    },
    "samambaia": {
        "umidade_min": 40, "umidade_max": 70,
        "temperatura_min": 12, "temperatura_max": 31,
        "luz": "alta"
    },
    "pimentao": {
        "umidade_min": 55, "umidade_max": 75,
        "temperatura_min": 18, "temperatura_max": 30,
        "luz": "alta"
    },
    "pepino": {
        "umidade_min": 60, "umidade_max": 85,
        "temperatura_min": 18, "temperatura_max": 32,
        "luz": "alta"
    },
    "brocolis": {
        "umidade_min": 45, "umidade_max": 75,
        "temperatura_min": 10, "temperatura_max": 22,
        "luz": "media"
    },
    "espinafre": {
        "umidade_min": 50, "umidade_max": 80,
        "temperatura_min": 8, "temperatura_max": 22,
        "luz": "media"
    },
    "rucula": {
        "umidade_min": 40, "umidade_max": 70,
        "temperatura_min": 10, "temperatura_max": 24,
        "luz": "media"
    },
    # Frutas tropicais
    "banana": {
        "umidade_min": 60, "umidade_max": 85,
        "temperatura_min": 20, "temperatura_max": 35,
        "luz": "alta"
    },
    "mamao": {
        "umidade_min": 50, "umidade_max": 80,
        "temperatura_min": 22, "temperatura_max": 35,
        "luz": "alta"
    },
    "abacaxi": {
        "umidade_min": 40, "umidade_max": 70,
        "temperatura_min": 20, "temperatura_max": 35,
        "luz": "alta"
    },
    "manga": {
        "umidade_min": 40, "umidade_max": 75,
        "temperatura_min": 22, "temperatura_max": 38,
        "luz": "alta"
    },
    "maracuja": {
        "umidade_min": 55, "umidade_max": 80,
        "temperatura_min": 18, "temperatura_max": 32,
        "luz": "alta"
    },
    "goiaba": {
        "umidade_min": 45, "umidade_max": 75,
        "temperatura_min": 20, "temperatura_max": 35,
        "luz": "alta"
    },
    "acerola": {
        "umidade_min": 40, "umidade_max": 70,
        "temperatura_min": 20, "temperatura_max": 35,
        "luz": "alta"
    },
}

def popular():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS plantas (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) UNIQUE,
            umidade_min FLOAT,
            umidade_max FLOAT,
            temperatura_min FLOAT,
            temperatura_max FLOAT,
            luz VARCHAR(20)
        )
    """)

    for nome, dados in plantas.items():
        cur.execute("""
            INSERT INTO plantas (nome, umidade_min, umidade_max, temperatura_min, temperatura_max, luz)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (nome) DO UPDATE SET
                umidade_min = EXCLUDED.umidade_min,
                umidade_max = EXCLUDED.umidade_max,
                temperatura_min = EXCLUDED.temperatura_min,
                temperatura_max = EXCLUDED.temperatura_max,
                luz = EXCLUDED.luz
        """, (nome, dados["umidade_min"], dados["umidade_max"],
              dados["temperatura_min"], dados["temperatura_max"], dados["luz"]))
        print(f"✅ {nome} inserida/atualizada")

    conn.commit()
    cur.close()
    conn.close()
    print("\n✅ Banco populado com sucesso!")

if __name__ == "__main__":
    popular()