import os
import psycopg2
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def criar_tabela():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id SERIAL PRIMARY KEY,
            planta VARCHAR(100),
            umidade FLOAT,
            temperatura FLOAT,
            saude INTEGER,
            data TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

criar_tabela()

def salvar_dados(planta, umidade, temperatura, saude):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO historico (planta, umidade, temperatura, saude)
        VALUES (%s, %s, %s, %s)
    """, (planta, umidade, temperatura, saude))
    conn.commit()
    cur.close()
    conn.close()

def carregar_dados():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT planta, umidade, temperatura, saude, data FROM historico ORDER BY data ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "planta": r[0],
            "umidade": r[1],
            "temperatura": r[2],
            "saude": r[3],
            "data": r[4].isoformat()
        }
        for r in rows
    ]