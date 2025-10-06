import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from utils import load_data, apply_filters

st.title("Buts par match — par ligue (boxplot + jitter)")

df = load_data("top5playersclean.csv")

leagues = sorted(df["Comp"].dropna().unique().tolist())
positions = sorted(df["Pos"].dropna().unique().tolist())
sel_leagues = st.sidebar.multiselect("Ligues (Comp)", leagues, default=leagues)
sel_positions = st.sidebar.multiselect("Postes (Pos)", positions, default=positions)
min_mp = st.sidebar.slider("Seuil minimum de matchs (MP)", 0, int(df["MP"].max()), 5, 1)
remove_outliers = st.sidebar.checkbox("Retirer outliers (goals_per_match ≥ 5)", True)

data = apply_filters(df, sel_leagues, sel_positions, min_mp)
if {"Comp","goals_per_match"}.issubset(data.columns) and len(data)>0:
    d = data[["Comp","goals_per_match"]].dropna().copy()
    if remove_outliers:
        d = d[d["goals_per_match"] < 5]

    med = d.groupby("Comp")["goals_per_match"].median().sort_values(ascending=False)
    order = med.index.tolist()
    box_data = [d.loc[d["Comp"]==lg, "goals_per_match"].values for lg in order]

    if len(box_data):
        fig, ax = plt.subplots(figsize=(10,5))
        ax.boxplot(
            box_data, labels=order, patch_artist=True, showfliers=False,
            medianprops=dict(color="black", linewidth=1.5),
            boxprops=dict(facecolor="#89C2D9", edgecolor="#2C7DA0"),
            whiskerprops=dict(color="#2C7DA0"),
            capprops=dict(color="#2C7DA0")
        )

        rng = np.random.default_rng(42)
        for i, lg in enumerate(order, start=1):
            vals = d.loc[d["Comp"]==lg, "goals_per_match"].values
            xj = rng.normal(loc=i, scale=0.06, size=len(vals))
            ax.scatter(xj, vals, color="gray", alpha=0.35, s=12, edgecolor="none")

        ax.set_title("Répartition des buts par match par ligue (MP ≥ seuil)")
        ax.set_xlabel("Ligue"); ax.set_ylabel("Buts par match")
        ax.grid(axis="y", linestyle=":", alpha=0.35)
        st.pyplot(fig)
    else:
        st.info("Pas assez de données pour le boxplot.")
else:
    st.warning("Colonnes nécessaires manquantes (Comp, goals_per_match).")

