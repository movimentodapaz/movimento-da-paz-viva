import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.graph_objects as go

from locales import pt, en, es, fr, zh, ru, ar


st.set_page_config(
    page_title="Mapa",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- IDIOMAS ----------
LANGS = {
    "pt": pt.TEXTS,
    "en": en.TEXTS,
    "es": es.TEXTS,
    "fr": fr.TEXTS,
    "zh": zh.TEXTS,
    "ru": ru.TEXTS,
    "ar": ar.TEXTS,
}

lang = st.session_state.get("lang", "pt")
T = LANGS.get(lang, pt.TEXTS)

# ---------- PATH BANCO ----------
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

# ---------- CONTEÚDO ----------
st.markdown(f"## {T['map_title']}")

df = pd.read_sql("SELECT * FROM pacificadores", get_conn())

if df.empty:
    st.info(T["empty_map"])
else:
    total = len(df)
    brasil = len(df[df["pais"].str.lower() == "brasil"])
    exterior = total - brasil

    c1, c2, c3 = st.columns(3)
    c1.metric("🌍 Total", total)
    c2.metric("🇧🇷 Brasil", brasil)
    c3.metric("🌎 Exterior", exterior)

    lat_plot = df["latitude"] + np.random.randn(len(df)) * 0.01
    lon_plot = df["longitude"] + np.random.randn(len(df)) * 0.01

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
        mapbox=dict(style="open-street-map", center=dict(lat=0, lon=0), zoom=1),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---------- BOTÃO VOLTAR ----------
if st.button("⬅️ Home", use_container_width=True):
    st.switch_page("streamlit_app.py")
