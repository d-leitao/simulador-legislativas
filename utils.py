from typing import Dict, List
import streamlit as st


def reset_values(votes_pct_adjusted, DEFAULT_PARTIES):
    return {p: round(float(votes_pct_adjusted[p]), 1) for p in DEFAULT_PARTIES}

def render_input_row(parties: List[str], cols, NON_PARTY_VOTES, percentages):
    for i, party in enumerate(parties):
        with cols[i]:
            help_text = f"Outros partidos + {' + '.join(NON_PARTY_VOTES)}" if party == "Outros" else None
            percentages[party] = st.number_input(
                f"{party}",
                min_value=0.0,
                max_value=100.0,
                value=float(percentages[party]),
                step=0.1,
                format="%.1f",
                key=f"input_{party}",
                help=help_text,
                label_visibility="visible",
            )
    return percentages
