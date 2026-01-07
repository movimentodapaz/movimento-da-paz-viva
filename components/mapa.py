import sqlite3
import pandas as pd
import plotly.express as px
from pathlib import Path
import streamlit as st


# ---------- RESOLUÇÃO SEGURA DO CAMINHO DO BANCO ----------
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "pacificadores.db"


def get_conn():
    if not DB_PATH.exists():
        st.error(f"Banco de dados não encontrado em: {DB_PATH}")
        st.stop()
    return sqlite3.connect(DB_PATH)


def render_mapa():
    # ---------- LEITURA DO BANCO ----------
    df = pd.read_sql("SELECT * FROM pacificadores", get_conn())

    if df.empty:
        st.info("Ainda não há pacificadores registrados.")
        return

    # ---------- CONTADORES ----------
    total = len(df)
    brasil = len(df[df["pais"].str.lower() == "brasil"])
    exterior = total - brasil

    col1, col2, col3 = st.columns(3)
    col1.metric("🌍 Total", total)
    col2.metric("🇧🇷 Brasil", brasil)
    col3.metric("🌎 Exterior", exterior)

    # ---------- JITTER PARA PRIVACIDADE ----------
    df["lat_plot"] = df["latitude"] + (pd.Series(pd.np.random.randn(len(df))) * 0.01)
    df["lon_plot"] = df["longitude"] + (pd.Series(pd.np.random.randn(len(df))) * 0.01)

    # ---------- MAPA ----------
    fig = px.scatter_mapbox(
        df,
        lat="lat_plot",
        lon="lon_plot",
        hover_name="cidade",
        zoom=1,
        height=600
    )

    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox=dict(
            center=dict(lat=0, lon=0),
            zoom=1
        )
    )

    st.plotly_chart(fig, use_container_width=True)
