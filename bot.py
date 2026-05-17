import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def enviar_alerta(planta: str, umidade: float, temperatura: float, saude: int, recomendacoes: list):
    if saude >= 100:
        return  # Condições ideais, não envia alerta

    emoji_saude = "🟢" if saude >= 70 else "🟡" if saude >= 50 else "🔴"

    recomendacoes_texto = "\n".join([f"  • {r}" for r in recomendacoes])

    mensagem = (
        f"🌱 *Alerta da Horta Inteligente*\n\n"
        f"🪴 *Planta:* {planta.capitalize()}\n"
        f"💧 *Umidade do solo:* {umidade}%\n"
        f"🌡️ *Temperatura:* {temperatura}°C\n"
        f"{emoji_saude} *Saúde:* {saude}/100\n\n"
        f"📋 *Recomendações:*\n{recomendacoes_texto}"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Erro ao enviar alerta no Telegram: {e}")