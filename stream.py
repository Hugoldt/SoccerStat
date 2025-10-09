import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.set_page_config(page_title="SoccerStat Dashboard", page_icon="⚽", layout="wide")

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if {"Gls", "MP"}.issubset(df.columns):
        df["goals_per_match"] = (df["Gls"] / df["MP"]).replace([float("inf"), -float("inf")], 0).fillna(0)
    if {"Ast", "MP"}.issubset(df.columns):
        df["assists_per_match"] = (df["Ast"] / df["MP"]).replace([float("inf"), -float("inf")], 0).fillna(0)
    if {"Gls", "Min"}.issubset(df.columns):
        df["Gls_90"] = (df["Gls"] / df["Min"] * 90).replace([float("inf"), -float("inf")], 0).fillna(0)
    if {"Ast", "Min"}.issubset(df.columns):
        df["Ast_90"] = (df["Ast"] / df["Min"] * 90).replace([float("inf"), -float("inf")], 0).fillna(0)
    return df

DATA_PATH = "top5playersclean.csv"
df = load_data(DATA_PATH)

st.title("SoccerStat Dashboard")
st.caption("Tous les graphiques du notebook `cleaningcsvfoot.ipynb` intégrés")

col1, col2, col3, col4 = st.columns(4)
with col1:
    leagues = st.multiselect("Ligues", sorted(df["Comp"].dropna().unique().tolist()) if "Comp" in df else [],
                             default=sorted(df["Comp"].dropna().unique().tolist()) if "Comp" in df else [])
with col2:
    positions = st.multiselect("Positions", sorted(df["Pos"].dropna().unique().tolist()) if "Pos" in df else [],
                               default=sorted(df["Pos"].dropna().unique().tolist()) if "Pos" in df else [])
with col3:
    min_goals = st.slider("Buts min", 0, int(df["Gls"].max()) if "Gls" in df else 0, 0)
with col4:
    min_assists = st.slider("Assists min", 0, int(df["Ast"].max()) if "Ast" in df else 0, 0)

df_filtered = df.copy()
if "Comp" in df_filtered and leagues:
    df_filtered = df_filtered[df_filtered["Comp"].isin(leagues)]
if "Pos" in df_filtered and positions:
    df_filtered = df_filtered[df_filtered["Pos"].isin(positions)]
if "Gls" in df_filtered:
    df_filtered = df_filtered[df_filtered["Gls"] >= min_goals]
if "Ast" in df_filtered:
    df_filtered = df_filtered[df_filtered["Ast"] >= min_assists]

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1: st.metric("Joueurs", len(df_filtered))
with col_m2: st.metric("Buts totaux", int(df_filtered["Gls"].sum()) if "Gls" in df_filtered else 0)
with col_m3: st.metric("Assists totaux", int(df_filtered["Ast"].sum()) if "Ast" in df_filtered else 0)
with col_m4: st.metric("Buts/Match moyen", f"{df_filtered.get('goals_per_match', pd.Series()).mean():.2f}" if "goals_per_match" in df_filtered else "0.00")

st.divider()

st.subheader("Graphique 3D - Buts vs Assists vs Minutes")
df_3d = df_filtered[df_filtered['MP'] >= 5].copy()

fig_3d = go.Figure(data=go.Scatter3d(
    x=df_3d['Gls'], 
    y=df_3d['Ast'], 
    z=df_3d['Min'],
    mode='markers',
    marker=dict(
        size=8,
        color=df_3d['MP'],
        colorscale='viridis',
        opacity=0.8
    ),
    text=df_3d['Player'],
    hovertemplate='<b>%{text}</b><br>Buts: %{x}<br>Assists: %{y}<br>Minutes: %{z}<br><extra></extra>'
))

fig_3d.update_layout(
    title="Relation 3D : Buts vs Assists vs Minutes",
    scene=dict(
        xaxis_title='Buts',
        yaxis_title='Assists',
        zaxis_title='Minutes'
    )
)
st.plotly_chart(fig_3d, use_container_width=True)

st.subheader("Performance par Tranche d'Âge")
if 'Age' in df_filtered.columns:
    df_filtered['age_group'] = pd.cut(df_filtered['Age'], 
                                    bins=[0, 22, 25, 28, 32, 50], 
                                    labels=['18-22', '23-25', '26-28', '29-32', '33+'])

    age_stats = df_filtered.groupby('age_group')[['Gls', 'Ast', 'Min', 'MP']].mean()

    fig_age = go.Figure()
    fig_age.add_trace(go.Bar(
        name='Buts moyens',
        x=age_stats.index,
        y=age_stats['Gls'],
        marker_color='#e74c3c',
        opacity=0.8
    ))
    fig_age.add_trace(go.Bar(
        name='Assists moyens',
        x=age_stats.index,
        y=age_stats['Ast'],
        marker_color='#3498db',
        opacity=0.8
    ))
    fig_age.add_trace(go.Bar(
        name='Minutes moyennes (x10)',
        x=age_stats.index,
        y=age_stats['Min']/10,
        marker_color='#2ecc71',
        opacity=0.8
    ))

    fig_age.update_layout(
        title="Performance Moyenne par Tranche d'Âge",
        xaxis_title="Tranche d'âge",
        yaxis_title="Valeurs moyennes",
        barmode='group'
    )
    st.plotly_chart(fig_age, use_container_width=True)

df_3d = df[df['MP'] >= 5].copy()

fig_3d = go.Figure(data=go.Scatter3d(
    x=df_3d['Gls'],
    y=df_3d['Ast'],
    z=df_3d['Min'],
    mode='markers',
    marker=dict(
        size=8,
        color=df_3d['MP'],
        colorscale='viridis',
        opacity=0.8,
        colorbar=dict(title="Matchs Joués")
    ),
    text=df_3d['Player'],
    hovertemplate='<b>%{text}</b><br>' +
                 'Buts: %{x}<br>' +
                 'Assists: %{y}<br>' +
                 'Minutes: %{z}<br>' +
                 '<extra></extra>'
))

fig_3d.update_layout(
    title="Relation 3D : Buts vs Assists vs Minutes",
    scene=dict(
        xaxis_title='Buts',
        yaxis_title='Assists',
        zaxis_title='Minutes'
    ),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_size=12
)

fig_3d.show()

df['age_group'] = pd.cut(df['Age'], 
                        bins=[0, 22, 25, 28, 32, 50], 
                        labels=['18-22', '23-25', '26-28', '29-32', '33+'])

age_stats = df.groupby('age_group')[['Gls', 'Ast', 'Min', 'MP']].mean()

fig_age = go.Figure()

fig_age.add_trace(go.Bar(
    name='Buts moyens',
    x=age_stats.index,
    y=age_stats['Gls'],
    marker_color='#e74c3c',
    opacity=0.8
))

fig_age.add_trace(go.Bar(
    name='Assists moyens',
    x=age_stats.index,
    y=age_stats['Ast'],
    marker_color='#3498db',
    opacity=0.8
))

fig_age.add_trace(go.Bar(
    name='Minutes moyennes (x10)',
    x=age_stats.index,
    y=age_stats['Min']/10,
    marker_color='#2ecc71',
    opacity=0.8
))

fig_age.update_layout(
    title="Performance Moyenne par Tranche d'Âge",
    xaxis_title="Tranche d'âge",
    yaxis_title="Valeurs moyennes",
    barmode='group',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_size=12
)

fig_age.show()