import requests
import os
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def obter_previsao_proximas_horas(cidade="Teresina"):
    # Mudamos o endpoint de /weather para /forecast
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?q={cidade},BR"
        f"&appid={OPENWEATHER_API_KEY}"
        f"&units=metric"
        f"&lang=pt_br"
    )

    resposta = requests.get(url)

    if resposta.status_code != 200:
        print("Erro ao acessar Forecast:", resposta.status_code)
        return None

    dados = resposta.json()
    
    # A lista 'list' contém as previsões. Vamos pegar as duas primeiras (próximas 6 horas)
    lista_previsoes = dados["list"]
    
    proxima_1 = lista_previsoes[0] # Daqui a ~3 horas
    proxima_2 = lista_previsoes[1] # Daqui a ~6 horas

    # Criamos uma lógica simples: se vai chover em qualquer uma das duas janelas, consideramos que vai chover logo
    chuva_prevista = False
    descricoes = []
    temperaturas_ar = []

    for previsao in [proxima_1, proxima_2]:
        descricao = previsao["weather"][0]["description"].lower()
        descricoes.append(descricao)
        temperaturas_ar.append(previsao["main"]["temp"])
        
        # Se houver menção a chuva ou se o parâmetro 'pop' (probabilidade de precipitação) for alto
        # Nota: 'pop' vai de 0 (0%) a 1 (100%) nas versões mais novas da API
        pop = previsao.get("pop", 0) 
        if "chuva" in descricao or "chuvisco" in descricao or pop > 0.5:
            chuva_prevista = True

    # Retornamos a média de temperatura das próximas horas e se há previsão de chuva
    return {
        "temperatura_ar_futura": sum(temperaturas_ar) / len(temperaturas_ar),
        "vai_chover_logo": chuva_prevista,
        "descricao_futura": ", ".join(set(descricoes)) # Remove duplicados e junta
    }