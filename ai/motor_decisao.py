from data.plantas import plantas

def calcular_saude_umidade(
    umidade,
    minimo,
    maximo
):

    # faixa ideal
    if minimo <= umidade <= maximo:
        return 100

    # abaixo do mínimo
    if umidade < minimo:

        diferenca = minimo - umidade

        return max(
            0,
            100 - diferenca * 2
        )

    # acima do máximo
    diferenca = umidade - maximo

    return max(
        0,
        100 - diferenca * 2
    )

def calcular_saude_temperatura(
    temperatura,
    minimo,
    maximo
):

    if minimo <= temperatura <= maximo:
        return 100

    if temperatura < minimo:

        diferenca = minimo - temperatura

        return max(
            0,
            100 - diferenca * 5
        )

    diferenca = temperatura - maximo

    return max(
        0,
        100 - diferenca * 5
    )

def analisar_planta(planta, umidade, temperatura):

    planta = planta.lower()

    if planta not in plantas:
        return 0, ["Planta não cadastrada"]

    dados = plantas[planta]

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

    saude = int(
        (saude_umidade + saude_temperatura) / 2
    )

    # recomendações de umidade

    if umidade < dados["umidade_min"]:
        recomendacoes.append(
            "Solo seco → irrigar"
        )

    elif umidade > dados["umidade_max"]:
        recomendacoes.append(
            "Solo encharcado → reduzir irrigação"
        )

    # recomendações de temperatura

    if temperatura < dados["temperatura_min"]:
        recomendacoes.append(
            "Temperatura baixa → proteger planta"
        )

    elif temperatura > dados["temperatura_max"]:
        recomendacoes.append(
            "Temperatura alta → reduzir exposição ao calor"
        )

    if len(recomendacoes) == 0:
        recomendacoes.append(
            "Condições ideais"
        )

    return saude, recomendacoes
print("MOTOR V2 ATIVO")