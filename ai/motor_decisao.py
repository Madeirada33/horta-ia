from data.plantas import plantas

def analisar_planta(planta, umidade, temperatura):

    planta = planta.lower()

    if planta not in plantas:
        return 0, ["Planta não cadastrada"]

    dados = plantas[planta]

    recomendacoes = []
    saude = 100

    if umidade < dados["umidade_minima"]:
        recomendacoes.append("Solo seco → irrigar")
        saude -= 30

    if temperatura < dados["temperatura_min"]:
        recomendacoes.append("Temperatura baixa → proteger planta")
        saude -= 20

    if temperatura > dados["temperatura_max"]:
        recomendacoes.append("Temperatura alta → reduzir sol")
        saude -= 20

    if len(recomendacoes) == 0:
        recomendacoes.append("Condições ideais")

    return saude, recomendacoes