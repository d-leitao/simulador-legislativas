import streamlit as st
import pandas as pd
import numpy as np

from calc import (
    calcular_percentagens_ajustadas,
    calcular_indices_regionais,
    simular_votos,
    calcular_resultados_finais
)

st.set_page_config()
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("## Simulador Legislativas 2025")

voto = pd.read_csv('2024.csv', sep=';')
votos_prev = (
    voto.replace("c.r.", "0")
        .replace("-", "0")
        .set_index('Partido')
        .astype(float)
)

default_parties = ["PSD", "PS", "CH", "IL", "BE", "PCP", "L", "PAN", "Outros"]
votos_pct_adjusted = calcular_percentagens_ajustadas(votos_prev, default_parties)

percentages = {}
num_columns = 5
rows = [default_parties[i:i + num_columns] for i in range(0, len(default_parties), num_columns)]
for row in rows:
    cols = st.columns(num_columns)
    for i, party in enumerate(row):
        default_value = float(votos_pct_adjusted[party])
        percentages[party] = cols[i].number_input(
            f"{party}",
            min_value=0.0,
            max_value=100.0,
            value=default_value,
            step=0.1,
            format="%.1f",
            key=f"input_{party}"
        )

with st.sidebar:
    st.markdown("### Opções")
    if st.button("↺ Reset para valores anteriores", help="Reverter para resultados da última eleição"):
        st.session_state.clear()
        st.rerun()

total_percent = round(sum(percentages.values()), 1)
st.markdown("---")
msg = f"Total: {total_percent}%"
if total_percent == 100.0:
    st.sidebar.success(msg)
else:
    st.sidebar.warning(msg)
    st.stop()

elections_df = votos_prev.astype(float)
indices_regionais = calcular_indices_regionais(elections_df, default_parties)
simulated_votes = simular_votos(percentages, indices_regionais, elections_df, default_parties)
final_results, circle_results = calcular_resultados_finais(simulated_votes, default_parties)

results_df = pd.DataFrame.from_dict(final_results, orient='index', columns=['Mandatos']).sort_values('Mandatos', ascending=False)
results_df.loc['Total'] = results_df['Mandatos'].sum()
st.write(results_df)
