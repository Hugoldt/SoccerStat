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