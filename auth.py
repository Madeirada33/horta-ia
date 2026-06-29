import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "coop_habitat_chave_secreta")
ALGORITHM = "HS256"
EXPIRACAO_HORAS = 24

def criar_token(usuario_id: int, nome: str, email: str) -> str:
    expiracao = datetime.utcnow() + timedelta(hours=EXPIRACAO_HORAS)
    payload = {
        "sub": str(usuario_id),
        "nome": nome,
        "email": email,
        "exp": expiracao
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None