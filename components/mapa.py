import sqlite3
import pandas as pd
import plotly.express as px
from pathlib import Path
import streamlit as st
import numpy as np


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

    if df.empty:
        st.info("Ainda não há pacificadores registrados no mapa.")
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
    df["lat_plot"] = df["latitude"] + np.random.randn(len(df)) * 0.01
    df["lon_plot"] = df["longitude"] + np.random.randn(len(df)) * 0.01

    # ---------- MAPA ----------
    fig = px.scatter_mapbox(
        df,
        lat="lat_plot",
        lon="lon_plot",
        hover_name="cidade",
        zoom=1,
        height=600,
        color_discrete_sequence=["#FFD700"]  # 🌞 AMARELO DOURADO (SOL)
    )

    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox=dict(center=dict(lat=0, lon=0), zoom=1)
    )

    st.plotly_chart(fig, use_container_width=True)
