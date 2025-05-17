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

st.markdown("## Simulador Legislativas 2025 🗳")
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

# Function to handle automatic adjustments
def adjust_other_parties(changed_party, new_value, old_values):
    """Update party percentages while maintaining 100% total."""
    new_values = old_values.copy()
    new_value = round(new_value, 1)  # Ensure new value is rounded
    new_values[changed_party] = new_value
    
    # Calculate how much we need to adjust
    delta = new_value - old_values[changed_party]
    
    if abs(delta) > 0.001:  # Only adjust if there's a meaningful change
        # Get sum of other parties (excluding the changed one)
        other_parties = [p for p in old_values.keys() if p != changed_party]
        other_sum = sum(old_values[p] for p in other_parties)
        
        if other_sum > 0:  # Only adjust if there's something to adjust
            # Adjust proportionally
            for party in other_parties:
                proportion = old_values[party] / other_sum
                adjustment = delta * proportion
                # For increases we subtract, for decreases we add
                new_values[party] = round(old_values[party] - adjustment, 1)
                new_values[party] = max(0, new_values[party])  # Ensure no negative values
    
    # Final adjustment to ensure exactly 100%
    total = sum(new_values.values())
    if total != 100:
        # Add/subtract the difference from the largest party that's not the changed one
        largest_party = max((p for p in other_parties), key=lambda p: new_values[p])
        new_values[largest_party] = round(new_values[largest_party] + (100 - total), 1)
    
    return new_values

# Initialize session state
if 'percentages' not in st.session_state:
    st.session_state.percentages = {p: round(float(votes_pct_adjusted[p]), 1) for p in default_parties}

def handle_input_change():
    """Call this function when any input changes"""
    # Find which input changed by comparing with session state
    for party in default_parties:
        if f"input_{party}" in st.session_state:
            new_value = round(st.session_state[f"input_{party}"], 1)
            if abs(new_value - st.session_state.percentages[party]) >= 0.1:
                st.session_state.percentages = adjust_other_parties(party, new_value, st.session_state.percentages)
                break

def reset_values():
    """Reset all values to initial state"""
    st.session_state.percentages = {p: round(float(votes_pct_adjusted[p]), 1) for p in default_parties}
    st.experimental_rerun()

# Organize inputs in a tight grid - first row
cols = st.columns([1, 1, 1, 1, 1, 1])
percentages = {}

# First row
for i, party in enumerate(default_parties[:6]):
    with cols[i]:
        help_text = "Outros partidos + Votos em branco + Votos nulos" if party == "Outros" else None
        st.number_input(
            f"{party}",
            min_value=0.0,
            max_value=100.0,
            value=float(st.session_state.percentages[party]),
            step=0.1,
            format="%.1f",
            key=f"input_{party}",
            on_change=handle_input_change,
            help=help_text,
            label_visibility="visible"
        )
        percentages[party] = st.session_state.percentages[party]

# Second row
cols2 = st.columns([1, 1, 1, 1, 1, 1])

# Handle remaining parties
for i, party in enumerate(default_parties[6:]):
    with cols2[i]:
        help_text = "Outros partidos + Votos em branco + Votos nulos" if party == "Outros" else None
        st.number_input(
            f"{party}",
            min_value=0.0,
            max_value=100.0,
            value=float(st.session_state.percentages[party]),
            step=0.1,
            format="%.1f",
            key=f"input_{party}",
            on_change=handle_input_change,
            help=help_text,
            label_visibility="visible"
        )
        percentages[party] = st.session_state.percentages[party]

# Add reset button in the 4th column
with cols2[3]:
    st.write("")  # Add some spacing
    if st.button("Reset", key="reset_button"):
        reset_values()

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
    plot_df = plot_df[plot_df.index != 'Outros']
    fig = {
        'data': [{
            'x': plot_df.index,
            'y': plot_df['Mandatos'],
            'type': 'bar',
            'marker': {
                'color': ['#FF7F00', '#FF0000', '#18375F', '#0066FF', '#BE0026', '#C90A1E', '#00FFA3', '#33CC33']
            },
            'text': plot_df['Mandatos'],
            'textposition': 'outside',
            'textfont': {'size': 16},
        }],
        'layout': {
            'yaxis': {
                'title': 'Deputados',
                'title_font': {'size': 18},
                'tickfont': {'size': 14}
            },
            'xaxis': {
                'tickfont': {'size': 14}
            },
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
            'y': [''],            'orientation': 'h',
            'type': 'bar',
            'text': [f"{party} ({seats})"],
            'textposition': 'inside',
            'marker': {'color': party_colors[party]},
            'showlegend': False,
            'textfont': {'color': 'white', 'size': 14},
            'hovertemplate': party + ': %{x} deputados<extra></extra>'})
    
    fig_blocks = {
        'data': party_data,        'layout': {
            'barmode': 'stack',
            'showlegend': False,
            'xaxis': {
                'range': [0, 230],
                'showgrid': False,
                'showticklabels': False,
                'showline': False
            },
            'yaxis': {
                'showticklabels': False
            },
            'legend': {
                'x': 1.02,
                'y': 0.5,
                'xanchor': 'left',
                'yanchor': 'middle',
                'font': {'size': 14},
                'itemwidth': 30
            },
            'shapes': [{
                'type': 'line',
                'x0': 115,
                'x1': 115,
                'y0': -0.5,
                'y1': 0.5,                'line': {
                    'color': '#FF4500',
                    'width': 3,
                    'dash': 'dashdot'
                }            }],            'annotations': [{
                'x': 115,
                'y': 0.8,
                'text': '<b>Maioria (115)</b>',
                'showarrow': False,
                'font': {'size': 14, 'color': '#FF4500'},
                'yanchor': 'bottom'
            }],
            'bargap': 0,
            'bargroupgap': 0,
            'height': 120,
            'margin': {'l': 20, 'r': 20, 't': 10, 'b': 30}
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
            f"🔸 Esquerda (PS+BE+PCP+L+PAN): {left_block} deputados\n\n"
            f"🔸 CH: {ch_block} deputados\n\n"
            f"🔸 Direita (AD+IL): {right_block} deputados\n\n"
        )
