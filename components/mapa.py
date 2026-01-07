import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.graph_objects as go

# ---------- IDIOMA (SEGURO) ----------
T = st.session_state.get("texts", {
    "map_title": "Mapa",
    "empty_map": "Nenhum registro encontrado."
})

# ---------- PATH BANCO ----------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "pacificadores.db"

def get_conn():
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn

# ---------- FUNÇÃO PÚBLICA ----------
def render_mapa():
    st.markdown(f"## {T.get('map_title')}")

    try:
        df = pd.read_sql("SELECT * FROM pacificadores", get_conn())
    except Exception as e:
        st.error("Erro ao acessar o banco de dados.")
        return

    if df.empty:
        st.info(T.get("empty_map"))
        return

    # valida coordenadas
    df = df[
        df["latitude"].between(-90, 90) &
        df["longitude"].between(-180, 180)
    ]

    if df.empty:
        st.warning("Não há coordenadas válidas para exibir.")
        return

    # jitter mínimo
    jitter = 0.001
    lat = df["latitude"] + np.random.uniform(-jitter, jitter, len(df))
    lon = df["longitude"] + np.random.uniform(-jitter, jitter, len(df))

    fig = go.Figure(
        go.Scattermapbox(
            lat=lat,
            lon=lon,
            mode="markers",
            marker=dict(
                size=10,
                color="#FFD700",
                opacity=0.9
            ),
            text=df["cidade"],
            hoverinfo="text"
        )
    )

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=0, lon=0),
            zoom=1
        ),
        margin=dict(r=0, t=0, l=0, b=0),
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)
