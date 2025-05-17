import streamlit as st
import pandas as pd
import numpy as np

from calc import (
    calculate_adjusted_percentages,
    calculate_regional_proportions,
    simulate_national_votes,
    calculate_final_results
)

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("## Simulador Legislativas 2025")
prev_elections_raw = pd.read_csv('2024.csv', sep=';')
prev_elections = (
    prev_elections_raw
    .replace("c.r.", "0")
    .replace("-", "0")
    .set_index('Partido')
    .astype(float)
)

default_parties = ["PSD", "PS", "CH", "IL", "BE", "PCP", "L", "PAN", "Outros"]
votes_pct_adjusted = calculate_adjusted_percentages(prev_elections, default_parties)

with st.form("input_form"):    
    # Organize inputs in a wider grid
    percentages = {}
    num_cols = 5
    for i in range(0, len(default_parties), num_cols):
        cols = st.columns(num_cols)
        for j, party in enumerate(default_parties[i:i + num_cols]):
            if j < len(default_parties[i:i + num_cols]):
                with cols[j]:
                    default_value = float(votes_pct_adjusted[party])
                    help_text = "Outros partidos + Votos em branco + Votos nulos" if party == "Outros" else None
                    percentages[party] = st.number_input(
                        f"{party}",
                        min_value=0.0,
                        max_value=100.0,
                        value=default_value,
                        step=0.1,
                        format="%.1f",
                        help=help_text,
                        key=f"input_{party}"
                    )
    
    # Total and submit in the same row
    col_total, col_submit = st.columns([4, 1])
    with col_total:
        total_percent = round(sum(percentages.values()), 1)
        msg = f"Total: {total_percent}%"
        if total_percent == 100.0:
            st.success(msg)
        else:
            st.error(msg)
    
    with col_submit:
        submit = st.form_submit_button("Calcular")
        if not submit and total_percent != 100.0:
            st.stop()

# Results section
elections_df = prev_elections.astype(float)
regional_proportions = calculate_regional_proportions(elections_df, default_parties)
simulated_votes = simulate_national_votes(percentages, regional_proportions, elections_df, default_parties)
final_results, district_results = calculate_final_results(simulated_votes, default_parties)

# Results visualization
results_df = pd.DataFrame.from_dict(final_results, orient='index', columns=['Mandatos']).sort_values('Mandatos', ascending=False)

# Calculate potential parliamentary blocks
right_block = results_df.loc[["PSD", "IL"], "Mandatos"].sum() if "Total" not in results_df.loc[["PSD", "IL"]].index else 0
ch_block = results_df.loc["CH", "Mandatos"]
left_block = results_df.loc[["PS", "BE", "PCP", "L", "PAN"], "Mandatos"].sum() if "Total" not in results_df.loc[["PS", "BE", "PCP", "L", "PAN"]].index else 0

# Show results in plots
col_barplot, col_blocks = st.columns(2)

with col_barplot:
    plot_df = results_df.copy()
    fig = {
        'data': [{
            'x': plot_df.index,
            'y': plot_df['Mandatos'],
            'type': 'bar',
            'marker': {
                'color': ['#FF7F00', '#FF0000', '#18375F', '#0066FF', '#BE0026', '#C90A1E', '#00FFA3', '#33CC33', '#999999']
            },
            'text': plot_df['Mandatos'],
            'textposition': 'auto',
        }],
        'layout': {
            'yaxis': {'title': 'Número de deputados'},
            'height': 400,
            'margin': {'t': 20}
        }
    }
    st.plotly_chart(fig, use_container_width=True)

with col_blocks:
    
    # Create single-line parliament visualization
    party_data = []
    
    # Define all parties in the desired order and their colors
    party_order = ["PCP", "BE", "L", "PS", "PAN", "CH", "PSD", "IL"]
    party_colors = {
        'PCP': '#C90A1E',
        'BE': '#BE0026',
        'L': '#00FFA3',
        'PS': '#FF0000',
        'PAN': '#33CC33',
        'CH': '#18375F',
        'PSD': '#FF7F00',
        'IL': '#0066FF'
    }
    
    # Create bars for all parties in the specified order
    for party in party_order:
        seats = results_df.loc[party, "Mandatos"] if party in results_df.index else 0
        party_data.append({
            'name': party,
            'x': [seats],
            'y': [''],
            'orientation': 'h',
            'type': 'bar',
            'text': str(seats),
            'textposition': 'auto',
            'marker': {'color': party_colors[party]},
            'hovertemplate': party + ': %{x} deputados<extra></extra>'        })
    
    fig_blocks = {
        'data': party_data,
        'layout': {
            'barmode': 'stack',
            'showlegend': False,            'xaxis': {
                'range': [0, 230],
                'showgrid': False,
                'showticklabels': False,
                'showline': False
            },
            'yaxis': {
                'showticklabels': False
            },            'shapes': [{
                'type': 'line',
                'x0': 115,
                'x1': 115,
                'y0': -0.5,
                'y1': 0.5,
                'line': {
                    'color': '#FFA500',
                    'width': 3,
                    'dash': 'dashdot'
                }            }],            'annotations': [{
                'x': 115,
                'y': 0.8,
                'text': '<b>Maioria (115)</b>',
                'showarrow': False,
                'font': {'size': 14, 'color': '#FFA500'},
                'yanchor': 'bottom'
            }],
            'bargap': 0,
            'bargroupgap': 0,
            'height': 120,
            'margin': {'l': 20, 'r': 20, 't': 10, 'b': 10}
        }
    }
    st.plotly_chart(fig_blocks, use_container_width=True)
    
    # Show scenario analysis
    majority_seats = 115
    if right_block >= majority_seats:
        st.success(f"🔹 AD+IL têm maioria absoluta (+{right_block - majority_seats} deputados)")
    elif left_block >= majority_seats:
        st.success(f"🔹 Esquerda tem maioria absoluta (+{left_block - majority_seats} deputados)")
    else:
        st.info(
            f"**Cenários possíveis:**\n"
            f"🔸 Direita (AD+IL): {right_block} deputados\n"
            f"🔸 CH: {ch_block} deputados\n"
            f"🔸 Esquerda (PS+BE+PCP+L+PAN): {left_block} deputados"
        )
