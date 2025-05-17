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

def calculate_adjusted_percentages(prev_votes, default_parties):
    votes_sum = prev_votes.sum(axis=1)
    votes_pct = (votes_sum / votes_sum.sum() * 100).round(1)
    votes_pct_adjusted = pd.Series(0.0, index=default_parties)
    for party in default_parties[:-1]:
        votes_pct_adjusted[party] = round(votes_pct.get(party, 0.0), 1)
    votes_pct_adjusted["Outros"] = round(100 - votes_pct_adjusted[:-1].sum(), 1)
    return votes_pct_adjusted

def calculate_regional_proportions(elections_df, default_parties):
    """
    Calculate the proportion of votes per region within each party.
    """
    proportions = pd.DataFrame(0.0, index=default_parties, columns=elections_df.columns)
    
    for party in default_parties:
        if party == "Outros":
            other_votes = elections_df.loc[~elections_df.index.isin(default_parties[:-1])].sum()
            total_other = other_votes.sum()
            proportions.loc[party] = other_votes / total_other if total_other > 0 else 1.0 / len(elections_df.columns)
        elif party in elections_df.index:
            votes = elections_df.loc[party]
            total = votes.sum()
            proportions.loc[party] = votes / total if total > 0 else 1.0 / len(elections_df.columns)
        else:
            proportions.loc[party] = 1.0 / len(elections_df.columns)

    return proportions.fillna(0.0)

def simulate_national_votes(percentages, regional_proportions, elections_df, default_parties):
    """
    Simulate votes per district, adjusting national totals while respecting regional distribution.
    """
    total_votes = elections_df.sum().sum()

    # Calculate desired total votes per party
    votes_per_party = {
        p: (percentages.get(p, 0) / 100) * total_votes
        for p in default_parties
    }

    simulated_votes = pd.DataFrame(0.0, index=default_parties, columns=elections_df.columns)

    for p in default_parties:
        distrib = regional_proportions.loc[p]
        simulated_votes.loc[p] = distrib * votes_per_party[p]

    return simulated_votes

def calculate_final_results(simulated_votes, default_parties):
    final_results = {p: 0 for p in default_parties}
    district_results = {}
    for district in simulated_votes.columns:
        votes_district = {p: simulated_votes.at[p, district] for p in default_parties if p != "Outros"}
        result = hondt_method(votes_district, seats_per_circle[district])
        district_results[district] = result
        for p, s in result.items():
            final_results[p] += s
    final_results["Outros"] = 0
    return final_results, district_results
