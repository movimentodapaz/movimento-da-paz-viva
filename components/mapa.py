# -*- coding: utf-8 -*-

import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.graph_objects as go


# ---------- TEXTOS SEGUROS (FALLBACK) ----------
TEXTS_FALLBACK = {
    "empty_map": "Ainda não há pacificadores registrados no mapa."
}


def get_text(key: str) -> str:
    """
    Busca texto do idioma ativo na sessão.
    Se não existir, usa fallback seguro.
    """
    texts = st.session_state.get("texts", {})
    return texts.get(key, TEXTS_FALLBACK.get(key, ""))


# ---------- PATH DO BANCO ----------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "pacificadores.db"


def get_conn():
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
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
    df = pd.read_sql("SELECT * FROM pacificadores", get_conn())

    if df.empty:
        st.info(get_text("empty_map"))
        return

    # ---------- CONTADORES ----------
    total = len(df)
    brasil = len(df[df["pais"].str.lower() == "brasil"])
    exterior = total - brasil

    c1, c2, c3 = st.columns(3)
    c1.metric("🌍 Total", total)
    c2.metric("🇧🇷 Brasil", brasil)
    c3.metric("🌎 Exterior", exterior)

    # ---------- JITTER ----------
    lat_plot = df["latitude"] + np.random.randn(len(df)) * 0.01
    lon_plot = df["longitude"] + np.random.randn(len(df)) * 0.01

    # ---------- MAPA ----------
    fig = go.Figure(
        go.Scattermapbox(
            lat=lat_plot,
            lon=lon_plot,
            mode="markers",
            marker=dict(
                size=10,
                color=["#FFD700"] * len(lat_plot),
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
