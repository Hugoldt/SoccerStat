import streamlit as st
from utils import load_data

st.set_page_config(page_title="SoccerStat Dashboard", layout="wide")
st.title("SoccerStat — Dashboard multi‑pages")

df = load_data("top5playersclean.csv")

st.markdown("- Naviguez vers les pages via le menu 'Pages' dans la barre latérale.")
st.markdown("- Les filtres spécifiques sont sur chaque page.")

with st.expander("Aperçu des données (100 premières lignes)"):
    st.dataframe(df.head(100), use_container_width=True)


