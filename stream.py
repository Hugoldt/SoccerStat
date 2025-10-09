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
st.subheader("Graphiques de Base du Notebook")

col_basic1, col_basic2 = st.columns(2)
with col_basic1:
    if 'Pos' in df_filtered.columns:
        pos_counts = df_filtered['Pos'].value_counts()
        fig_pos = px.bar(x=pos_counts.index, y=pos_counts.values, 
                        title="Nombre de joueurs par position", 
                        color=pos_counts.values, color_continuous_scale='Blues')
        fig_pos.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pos, use_container_width=True)

with col_basic2:
    if 'Nation' in df_filtered.columns:
        top_nations = df_filtered['Nation'].value_counts().head(15)
        fig_nations = px.bar(x=top_nations.values, y=top_nations.index, orientation='h',
                            title="Top 15 des nations (nombre de joueurs)",
                            color=top_nations.values, color_continuous_scale='Greens')
        fig_nations.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_nations, use_container_width=True)

st.subheader("Statistiques par Ligue")
if 'Comp' in df_filtered.columns and 'Gls' in df_filtered.columns:
    by_league = df_filtered.groupby("Comp")[["Gls","Ast","Min"]].sum().sort_values("Gls", ascending=False)
    
    col_league1, col_league2, col_league3 = st.columns(3)
    
    with col_league1:
        fig_gls = px.bar(x=by_league.index, y=by_league["Gls"], 
                        title="Buts totaux par ligue",
                        color=by_league["Gls"], color_continuous_scale='Reds')
        fig_gls.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_gls, use_container_width=True)
    
    with col_league2:
        fig_ast = px.bar(x=by_league.index, y=by_league["Ast"], 
                        title="Assists totales par ligue",
                        color=by_league["Ast"], color_continuous_scale='Blues')
        fig_ast.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_ast, use_container_width=True)
    
    with col_league3:
        fig_min = px.bar(x=by_league.index, y=by_league["Min"], 
                        title="Minutes totales par ligue",
                        color=by_league["Min"], color_continuous_scale='Purples')
        fig_min.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_min, use_container_width=True)

st.subheader("Top Performers")
if 'goals_per_match' in df_filtered.columns and 'MP' in df_filtered.columns:
    subset = df_filtered[df_filtered["MP"] >= 5].copy()
    if len(subset) > 0:
        top_goals_per_match = subset.nlargest(10, "goals_per_match")
        fig_top_goals = px.bar(x=top_goals_per_match["goals_per_match"], 
                              y=top_goals_per_match["Player"],
                              orientation='h',
                              title="Top 10 — Buts par match (MP ≥ 5)",
                              color=top_goals_per_match["goals_per_match"], 
                              color_continuous_scale='Oranges')
        fig_top_goals.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_top_goals, use_container_width=True)

st.subheader("Performance par 90 minutes par Position")
if all(col in df_filtered.columns for col in ['Pos', 'Gls_90', 'Ast_90', 'MP']):
    data_90 = df_filtered[df_filtered["MP"] >= 5][["Pos", "Gls_90", "Ast_90"]].dropna()
    if len(data_90) > 0:
        means_90 = data_90.groupby("Pos")[["Gls_90", "Ast_90"]].mean().sort_values("Gls_90", ascending=False)
        
        fig_90 = go.Figure()
        fig_90.add_trace(go.Bar(
            name='Buts / 90',
            x=means_90.index,
            y=means_90['Gls_90'],
            marker_color='#e74c3c',
            opacity=0.8
        ))
        fig_90.add_trace(go.Bar(
            name='Assists / 90',
            x=means_90.index,
            y=means_90['Ast_90'],
            marker_color='#3498db',
            opacity=0.8
        ))
        
        fig_90.update_layout(
            title="Moyennes par 90 minutes par poste (MP ≥ 5)",
            xaxis_title="Position",
            yaxis_title="Moyenne par 90 minutes",
            barmode='group',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_90, use_container_width=True)

st.subheader("Tableau de Bord Final - Synthèse des Performances")

total_players = len(df_filtered)
total_goals = df_filtered['Gls'].sum() if 'Gls' in df_filtered else 0
total_assists = df_filtered['Ast'].sum() if 'Ast' in df_filtered else 0
avg_goals = df_filtered['Gls'].mean() if 'Gls' in df_filtered else 0
avg_assists = df_filtered['Ast'].mean() if 'Ast' in df_filtered else 0

if 'Gls' in df_filtered and 'Player' in df_filtered:
    top_scorer = df_filtered.loc[df_filtered['Gls'].idxmax(), 'Player']
    top_scorer_goals = df_filtered['Gls'].max()
else:
    top_scorer = "N/A"
    top_scorer_goals = 0

if 'Ast' in df_filtered and 'Player' in df_filtered:
    top_assister = df_filtered.loc[df_filtered['Ast'].idxmax(), 'Player']
    top_assister_assists = df_filtered['Ast'].max()
else:
    top_assister = "N/A"
    top_assister_assists = 0

col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
with col_metric1:
    st.metric("Total joueurs", f"{total_players:,}")
with col_metric2:
    st.metric("Total buts", f"{total_goals:,}")
with col_metric3:
    st.metric("Total assists", f"{total_assists:,}")
with col_metric4:
    st.metric("Moyenne buts/joueur", f"{avg_goals:.2f}")

col_metric5, col_metric6, col_metric7, col_metric8 = st.columns(4)
with col_metric5:
    st.metric("Moyenne assists/joueur", f"{avg_assists:.2f}")
with col_metric6:
    st.metric("Meilleur buteur", f"{top_scorer} ({top_scorer_goals} buts)")
with col_metric7:
    st.metric("Meilleur passeur", f"{top_assister} ({top_assister_assists} assists)")
with col_metric8:
    st.metric("Ligues", len(df_filtered['Comp'].unique()) if 'Comp' in df_filtered else 0)

col_final1, col_final2, col_final3 = st.columns(3)

with col_final1:
    if 'Gls' in df_filtered and 'Player' in df_filtered:
        top_scorers = df_filtered.nlargest(10, 'Gls')
        fig_top_scorers = px.bar(x=top_scorers['Gls'], y=top_scorers['Player'], orientation='h',
                                title="Top 10 Buteurs", color=top_scorers['Gls'], 
                                color_continuous_scale='Reds')
        fig_top_scorers.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_top_scorers, use_container_width=True)

with col_final2:
    if 'Ast' in df_filtered and 'Player' in df_filtered:
        top_assisters = df_filtered.nlargest(10, 'Ast')
        fig_top_assisters = px.bar(x=top_assisters['Ast'], y=top_assisters['Player'], orientation='h',
                                  title="Top 10 Passeurs", color=top_assisters['Ast'], 
                                  color_continuous_scale='Blues')
        fig_top_assisters.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_top_assisters, use_container_width=True)

with col_final3:
    if 'Comp' in df_filtered:
        league_counts = df_filtered['Comp'].value_counts()
        fig_league_pie = px.pie(values=league_counts.values, names=league_counts.index, 
                               title="Répartition par Ligue")
        fig_league_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_league_pie, use_container_width=True)

st.subheader("Tableau de Résultats")
display_cols = [c for c in ["Player","Pos","Comp","Nation","MP","Gls","Ast","Min","goals_per_match","assists_per_match"] if c in df_filtered.columns]
st.dataframe(df_filtered[display_cols].sort_values(display_cols[5] if len(display_cols) > 5 else display_cols[0], ascending=False),
             use_container_width=True)

st.success("Dashboard mis à jour avec les graphiques actuels du notebook `cleaningcsvfoot.ipynb` !")