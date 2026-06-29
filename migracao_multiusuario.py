import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Usando a URL do seu banco de dados
DATABASE_URL = os.getenv("DATABASE_PUBLIC_URL") or os.getenv("DATABASE_URL")

def executar_migracao():
    print("🚀 Iniciando a reestruturação do banco de dados para Multiusuário...")
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # 1. CRIAR TABELA DE USUÁRIOS
    print("🔹 Criando tabela 'usuarios'...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            senha_hash VARCHAR(255) NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. CRIAR TABELA DE PLANTAÇÕES (VINCULADA AO USUÁRIO)
    print("🔹 Criando tabela 'plantacoes'...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS plantacoes (
            id SERIAL PRIMARY KEY,
            usuario_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
            nome VARCHAR(100) NOT NULL,
            cidade VARCHAR(100) DEFAULT 'Teresina',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. CRIAR TABELA DE SENSORES (PONTE ENTRE ESP32, PLANTAÇÃO E REGRAS DA PLANTA)
    print("🔹 Criando tabela 'sensores'...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sensores (
            id_mac VARCHAR(50) PRIMARY KEY,
            plantacao_id INT REFERENCES plantacoes(id) ON DELETE CASCADE,
            nome_planta VARCHAR(100) REFERENCES plantas(nome) ON DELETE SET NULL,
            status VARCHAR(20) DEFAULT 'active',
            ultima_conexao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 4. CRIAR TABELA DE HISTÓRICO DE LEITURAS AVANÇADO (VINCULADO AO SENSOR)
    print("🔹 Criando tabela 'historico_leituras'...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS historico_leituras (
            id SERIAL PRIMARY KEY,
            sensor_id VARCHAR(50) REFERENCES sensores(id_mac) ON DELETE CASCADE,
            umidade_solo FLOAT NOT NULL,
            temperatura_solo FLOAT NOT NULL,
            saude INTEGER NOT NULL,
            recomendacoes TEXT[] DEFAULT '{}',
            data_hora TIMESTAMP DEFAULT NOW()
        )
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("\n✅ Estrutura multiusuário criada com sucesso no Railway!")

if __name__ == "__main__":
    executar_migracao()