import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from utils import load_data, apply_filters

st.title("Exploration — Buts vs Assists")

df = load_data("top5playersclean.csv")

# Filtres partagés
leagues = sorted(df["Comp"].dropna().unique().tolist())
positions = sorted(df["Pos"].dropna().unique().tolist())
sel_leagues = st.sidebar.multiselect("Ligues (Comp)", leagues, default=leagues)
sel_positions = st.sidebar.multiselect("Postes (Pos)", positions, default=positions)
min_mp = st.sidebar.slider("Seuil minimum de matchs (MP)", 0, int(df["MP"].max()), 5, 1)

data = apply_filters(df, sel_leagues, sel_positions, min_mp)
required = {"Player","Pos","Gls","Ast","Min"}
if not required.issubset(data.columns) or len(data)==0:
    st.warning("Colonnes manquantes ou pas de données après filtre.")
    st.stop()

d = data[list(required)].dropna()
if len(d)==0:
    st.info("Aucune donnée après NA drop.")
    st.stop()

# Couleurs par poste
cmap = plt.get_cmap("tab10")
pos_list = sorted(d["Pos"].unique())
pos_to_color = {p: cmap(i % 10) for i, p in enumerate(pos_list)}

# Échelle de taille
mn, mx = d["Min"].min(), d["Min"].max()
sizes = 40 + 260 * (d["Min"] - mn) / (mx - mn if mx > mn else 1)

# Régression
x = d["Gls"].values
y = d["Ast"].values
coef = None
if len(x) >= 2 and np.nanstd(x) > 0:
    coef = np.polyfit(x, y, deg=1)
    x_line = np.linspace(x.min(), x.max(), 200)
    y_line = coef[0]*x_line + coef[1]

fig, ax = plt.subplots(figsize=(8,5))
for p in pos_list:
    m = d["Pos"]==p
    ax.scatter(d.loc[m,"Gls"], d.loc[m,"Ast"], s=sizes[m],
               c=[pos_to_color[p]], alpha=0.7, edgecolor="white", linewidth=0.5, label=p)
if coef is not None:
    ax.plot(x_line, y_line, "--", color="black", linewidth=1.4, label="Régression")
ax.set_title("Buts vs Assists (MP ≥ seuil) — taille=minutes")
ax.set_xlabel("Buts (Gls)")
ax.set_ylabel("Assists (Ast)")
ax.grid(True, linestyle=":", alpha=0.35)
ax.legend(title="Poste", ncol=2, fontsize=9)
st.pyplot(fig)

st.caption("Top 10 buteurs annotés")
top10 = d.sort_values("Gls", ascending=False).head(10)
fig2, ax2 = plt.subplots(figsize=(8,5))
for p in pos_list:
    m = d["Pos"]==p
    ax2.scatter(d.loc[m,"Gls"], d.loc[m,"Ast"], s=sizes[m],
                c=[pos_to_color[p]], alpha=0.7, edgecolor="white", linewidth=0.5)
if coef is not None:
    ax2.plot(x_line, y_line, "--", color="black", linewidth=1.4)
for _, r in top10.iterrows():
    ax2.annotate(r["Player"], (r["Gls"], r["Ast"]), xytext=(5,3), textcoords="offset points", fontsize=8)
ax2.set_xlabel("Buts (Gls)"); ax2.set_ylabel("Assists (Ast)"); ax2.grid(True, linestyle=":", alpha=0.35)
st.pyplot(fig2)


