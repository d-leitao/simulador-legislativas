import pandas as pd
import numpy as np

seats_per_circle = {
    'Aveiro': 16, 'Beja': 3, 'Braga': 19, 'Bragança': 3, 'Castelo Branco': 4, 'Coimbra': 9,
    'Évora': 3, 'Faro': 9, 'Guarda': 3, 'Leiria': 10, 'Lisboa': 48, 'Portalegre': 2,
    'Porto': 40, 'Santarém': 9, 'Setúbal': 19, 'Viana do Castelo': 5, 'Vila Real': 5,
    'Viseu': 8, 'Açores': 5, 'Madeira': 6, 'Europa': 2, 'Fora da Europa': 2
}

def hondt_method(votes, seats):
    quotients = {party: [vote / (i + 1) for i in range(seats)] for party, vote in votes.items()}
    all_quotients = [(q, party) for party, q_list in quotients.items() for q in q_list]
    all_quotients.sort(reverse=True)
    results = {party: 0 for party in votes}
    for _, party in all_quotients[:seats]:
        results[party] += 1
    return results

def calcular_percentagens_ajustadas(votos_prev, default_parties):
    votos_sum = votos_prev.sum(axis=1)
    votos_pct = (votos_sum / votos_sum.sum() * 100).round(1)
    votos_pct_adjusted = pd.Series(0.0, index=default_parties)
    for party in default_parties[:-1]:
        votos_pct_adjusted[party] = round(votos_pct.get(party, 0.0), 1)
    votos_pct_adjusted["Outros"] = round(100 - votos_pct_adjusted[:-1].sum(), 1)
    return votos_pct_adjusted

def calcular_indices_regionais(elections_df, default_parties):
    votos_pct_regional = pd.DataFrame(0.0, index=default_parties, columns=elections_df.columns)
    for party in default_parties:
        if party == "Outros":
            outros_votos = elections_df.loc[~elections_df.index.isin(default_parties[:-1])]
            votos_pct_regional.loc[party] = outros_votos.sum() / elections_df.sum()
        elif party in elections_df.index:
            votos_pct_regional.loc[party] = elections_df.loc[party] / elections_df.sum()
        else:
            votos_pct_regional.loc[party] = 1.0 / len(elections_df.columns)
    votos_nacional = votos_pct_regional.mean(axis=1)
    return votos_pct_regional.div(votos_nacional, axis=0).fillna(1.0)

def simular_votos(percentages, indices_regionais, elections_df, default_parties):
    simulated_votes = pd.DataFrame(0.0, index=default_parties, columns=elections_df.columns)
    for circle in elections_df.columns:
        total_votes = elections_df[circle].sum()
        pct_ajustadas = {p: percentages[p] * indices_regionais.at[p, circle] for p in default_parties}
        soma = sum(pct_ajustadas.values())
        pct_normalizadas = {p: v/soma for p, v in pct_ajustadas.items()}
        for p in default_parties:
            simulated_votes.at[p, circle] = total_votes * pct_normalizadas[p]
    return simulated_votes

def calcular_resultados_finais(simulated_votes, default_parties):
    final_results = {p: 0 for p in default_parties}
    circle_results = {}
    for circle in simulated_votes.columns:
        votes_circle = {p: simulated_votes.at[p, circle] for p in default_parties if p != "Outros"}
        result = hondt_method(votes_circle, seats_per_circle[circle])
        circle_results[circle] = result
        for p, s in result.items():
            final_results[p] += s
    final_results["Outros"] = 0
    return final_results, circle_results
