import sqlite3
import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path
import plotly.graph_objects as go

from locales import pt, en


# ---------- IDIOMAS ----------
LANGS = {
    "pt": pt.TEXTS,
    "en": en.TEXTS,
}

# Se idioma já estiver na sessão (vindo da Home), usa.
# Caso contrário, assume português.
lang = st.session_state.get("lang", "pt")
T = LANGS.get(lang, pt.TEXTS)


# ---------- RESOLUÇÃO SEGURA DE PATH ----------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "pacificadores.db"


# ---------- GARANTE EXISTÊNCIA DO BANCO ----------
def get_conn():
    DATA_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pacificadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT,
            cidade TEXT,
            pais TEXT,
            latitude REAL,
            longitude REAL,
            device_id TEXT UNIQUE,
            data_registro TEXT
        )
    """)

    conn.commit()
    return conn


def render_mapa():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM pacificadores", conn)

    # ---------- TÍTULO DO MAPA (I18N) ----------
    st.markdown(f"## {T['map_title']}")

    if df.empty:
        st.info(T["empty_map"])
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
    lat_plot = df["latitude"] + np.random.randn(len(df)) * 0.01
    lon_plot = df["longitude"] + np.random.randn(len(df)) * 0.01

    # ---------- MAPA (COR SOLAR FIXA) ----------
    fig = go.Figure(
        go.Scattermapbox(
            lat=lat_plot,
            lon=lon_plot,
            mode="markers",
            marker=dict(
                size=10,
                color=["#FFD700"] * len(lat_plot),  # 🌞 dourado solar
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
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)
