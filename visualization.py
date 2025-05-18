import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def plot_parliament(results_df, party_order, party_colors, majority_seats):
    party_data = []
    for party in party_order:
        seats = results_df.loc[party, "Mandatos"] if party in results_df.index else 0
        party_data.append({
            'name': party,
            'x': [seats],
            'y': [''],
            'orientation': 'h',
            'type': 'bar',
            'text': [f"{party} ({seats})"],
            'textposition': 'inside',
            'marker': {'color': party_colors[party]},
            'showlegend': False,
            'textfont': {'color': 'white', 'size': 18},
            'hovertemplate': party + ': %{x} deputados<extra></extra>'
        })
    fig_blocks = {
        'data': party_data,
        'layout': {
            'barmode': 'stack',
            'showlegend': False,
            'xaxis': {
                'range': [0, 230],
                'showgrid': False,
                'showticklabels': False,
                'showline': False
            },
            'yaxis': {'showticklabels': False},
            'shapes': [{
                'type': 'line',
                'x0': majority_seats,
                'x1': majority_seats,
                'y0': -0.7,
                'y1': 0.7,
                'line': {'color': '#FF4500', 'width': 5, 'dash': 'dashdot'}
            }],
            'annotations': [{
                'x': majority_seats,
                'y': -0.9,
                'text': f'<b>Maioria ({majority_seats})</b>',
                'showarrow': False,
                'font': {'size': 18, 'color': '#FF4500'},
                'yanchor': 'top'
            }],
            'bargap': 0,
            'bargroupgap': 0,
            'height': 160,
            'margin': {'l': 20, 'r': 20, 't': 10, 'b': 40}
        }
    }
    st.plotly_chart(fig_blocks, use_container_width=True)

def plot_party_barplot(results_df, party_colors):
    plot_df = results_df.copy()
    plot_df = plot_df[plot_df.index != 'Outros']
    fig = {
        'data': [{
            'x': plot_df.index,
            'y': plot_df['Mandatos'],
            'type': 'bar',
            'marker': {'color': [party_colors[party] for party in plot_df.index]},
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
            'xaxis': {'tickfont': {'size': 14}},
            'height': 400,
            'margin': {'t': 20}
        }
    }
    st.plotly_chart(fig, use_container_width=True)

def plot_party_percent_barplot(results_df, party_colors, session_percentages):
    percent_df = results_df.copy()
    percent_df['Percentagem'] = [session_percentages.get(p, 0) for p in percent_df.index]
    percent_df = percent_df[percent_df.index != 'Outros']
    fig_pct = go.Figure()
    fig_pct.add_bar(
        x=percent_df.index,
        y=percent_df['Percentagem'],
        marker_color=[party_colors[party] for party in percent_df.index],
        text=percent_df['Percentagem'],
        textposition='outside',
        textfont={'size': 16},
        name='Percentagem de votos'
    )
    fig_pct.update_layout(
        yaxis_title='Percentagem de votos',
        yaxis_title_font={'size': 18},
        yaxis_tickfont={'size': 14},
        xaxis_tickfont={'size': 14},
        height=400,
        margin={'t': 20}
    )
    st.plotly_chart(fig_pct, use_container_width=True)

def show_parliamentary_insights(results_df, majority_seats):
    right_block = results_df.loc[["PSD", "IL"], "Mandatos"].sum() if "Total" not in results_df.loc[["PSD", "IL"]].index else 0
    ch_block = results_df.loc["CH", "Mandatos"]
    left_block = results_df.loc[["PS", "BE", "PCP", "L", "PAN"], "Mandatos"].sum() if "Total" not in results_df.loc[["PS", "BE", "PCP", "L", "PAN"]].index else 0

    if right_block >= majority_seats:
        st.success(f"🔹 AD+IL têm maioria absoluta (+{right_block - majority_seats} deputados).")
    else:
        if right_block > left_block:
            st.info("🔸 Se Chega se abstem, AD+IL conseguem passar legislação.")

    if left_block >= majority_seats:
        st.success(f"🔹 Esquerda tem maioria absoluta (+{left_block - majority_seats} deputados).")

    if right_block < majority_seats and left_block < majority_seats:
        st.info(
            f"🔸 Esquerda (PS+BE+PCP+L+PAN): {left_block} deputados\n\n"
            f"🔸 CH: {ch_block} deputados\n\n"
            f"🔸 Direita (PSD+IL): {right_block} deputados\n\n"
        )
