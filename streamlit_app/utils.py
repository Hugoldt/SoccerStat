import numpy as np
import pandas as pd
import streamlit as st

@st.cache_data
def load_data(path="top5playersclean.csv"):
    df = pd.read_csv(path)
    # Sécurisation basique
    if "goals_per_match" not in df and {"Gls","MP"}.issubset(df.columns):
        df["goals_per_match"] = np.where(df["MP"]>0, df["Gls"]/df["MP"], np.nan)
    if "assists_per_match" not in df and {"Ast","MP"}.issubset(df.columns):
        df["assists_per_match"] = np.where(df["MP"]>0, df["Ast"]/df["MP"], np.nan)
    if "minutes_per_match" not in df and {"Min","MP"}.issubset(df.columns):
        df["minutes_per_match"] = np.where(df["MP"]>0, df["Min"]/df["MP"], np.nan)
    return df

def apply_filters(df, leagues, positions, min_mp):
    f = df.copy()
    if leagues:
        f = f[f["Comp"].isin(leagues)]
    if positions:
        f = f[f["Pos"].isin(positions)]
    if "MP" in f:
        f = f[f["MP"] >= min_mp]
    return f


