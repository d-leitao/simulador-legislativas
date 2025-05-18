from typing import Dict, List
import streamlit as st
import pandas as pd
import yaml
from calc import (
    calculate_adjusted_percentages,
    calculate_regional_proportions,
    simulate_national_votes,
    calculate_final_results,
)
from utils import reset_values, render_input_row
from visualization import (
    plot_parliament,
    plot_party_barplot,
    show_parliamentary_insights,
    plot_party_percent_barplot,
)

with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

TITLE = config["title"]
DEFAULT_PARTIES = config["default_parties"]
NON_PARTY_VOTES = config["non_party_votes"]
MAJORITY_SEATS = config["majority_seats"]
PARTY_ORDER = config["party_visualization"]["order"]
PARTY_COLORS = config["party_visualization"]["colors"]
NUM_COLUMNS = config.get("input_columns", 7)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown(TITLE)

prev_elections_raw = pd.read_csv("2024.csv", sep=";")
prev_elections = (
    prev_elections_raw.replace(["c.r.", "-"], "0").set_index("Partido").astype(float)
)
votes_pct_adjusted = calculate_adjusted_percentages(prev_elections, DEFAULT_PARTIES)
percentages = {p: round(float(votes_pct_adjusted[p]), 1) for p in DEFAULT_PARTIES}

cols = st.columns([1] * NUM_COLUMNS)
percentages = render_input_row(
    DEFAULT_PARTIES[:NUM_COLUMNS], cols, NON_PARTY_VOTES, percentages
)

cols2 = st.columns([1] * NUM_COLUMNS)
parties_second_row = DEFAULT_PARTIES[NUM_COLUMNS:]
percentages = render_input_row(
    parties_second_row, cols2, NON_PARTY_VOTES, percentages
)

with cols2[NUM_COLUMNS - 1]:
    st.write("")
    if st.button("Reset", key="reset_button"):
        percentages = reset_values(votes_pct_adjusted, DEFAULT_PARTIES)
        st.experimental_rerun()

percent_total = round(sum(percentages.values()), 1)
if abs(percent_total - 100) > 0.01:
    st.error(f"Total: {percent_total}% (deve ser 100%)")

elections_df = prev_elections.astype(float)
regional_proportions = calculate_regional_proportions(elections_df, DEFAULT_PARTIES)
simulated_votes = simulate_national_votes(
    percentages, regional_proportions, elections_df, DEFAULT_PARTIES
)
final_results, district_results = calculate_final_results(
    simulated_votes, DEFAULT_PARTIES
)
results_df = pd.DataFrame.from_dict(
    final_results, orient="index", columns=["Mandatos"]
).sort_values("Mandatos", ascending=False)

plot_parliament(results_df, PARTY_ORDER, PARTY_COLORS, MAJORITY_SEATS)
col_barplot, col_insights = st.columns([1, 1])
with col_barplot:
    plot_party_barplot(results_df, PARTY_COLORS)
    plot_party_percent_barplot(results_df, PARTY_COLORS, percentages)
with col_insights:
    show_parliamentary_insights(results_df, MAJORITY_SEATS)

