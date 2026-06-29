import os
import psycopg2
from seguranca import gerar_senha_hash, verificar_senha

DATABASE_URL = os.getenv("DATABASE_PUBLIC_URL") or os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def criar_usuario(nome, email, senha_plana):
    senha_hash = gerar_senha_hash(senha_plana)
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO usuarios (nome, email, senha_hash)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, (nome, email, senha_hash))
        usuario_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return usuario_id
    except psycopg2.errors.UniqueViolation:
        print("❌ Erro: Este e-mail já está cadastrado.")
        return None
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        return None

def login_usuario(email, senha_plana):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, nome, senha_hash FROM usuarios WHERE email = %s
        """, (email,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return None
        usuario_id, nome, senha_hash = row
        if not verificar_senha(senha_plana, senha_hash):
            return None
        return {"id": usuario_id, "nome": nome, "email": email}
    except Exception as e:
        print(f"❌ Erro ao fazer login: {e}")
        return None