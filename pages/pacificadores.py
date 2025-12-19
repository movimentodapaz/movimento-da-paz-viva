import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from pathlib import Path
import random

# =====================
# CONFIG
# =====================
st.set_page_config(layout="wide")

DB_PATH = Path("data/pacificadores.db")
DB_PATH.parent.mkdir(exist_ok=True)

# =====================
# DB SETUP
# =====================
def get_conn():
    return sqlite3.connect(DB_PATH)

def ensure_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pacificadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cidade TEXT,
            pais TEXT,
            latitude REAL,
            longitude REAL,
            data_registro TEXT
        )
    """)
    conn.commit()
    conn.close()

ensure_db()

# =====================
# JITTER VISUAL
# =====================
def jitter(lat, lon, radius_m=1500):
    r = radius_m / 111_000
    return (
        lat + random.uniform(-r, r),
        lon + random.uniform(-r, r)
    )

# =====================
# LOAD DATA
# =====================
def load_data():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM pacificadores", conn)
    conn.close()
    return df

df = load_data()

# =====================
# TÍTULO (MAPA EM DESTAQUE)
# =====================
st.markdown("<h1 style='margin-top:-60px'>Mapa dos Pacificadores da Paz Viva</h1>", unsafe_allow_html=True)

# =====================
# MAPA
# =====================
if df.empty:
    st.info("Ainda não há pacificadores registrados.")
else:
    df["lat_plot"], df["lon_plot"] = zip(*df.apply(
        lambda r: jitter(r.latitude, r.longitude), axis=1
    ))

    fig = px.density_mapbox(
        df,
        lat="lat_plot",
        lon="lon_plot",
        radius=10,
        zoom=1.3,
        center=dict(lat=-14.2, lon=-51.9),
        mapbox_style="carto-darkmatter",
        opacity=0.9
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

# =====================
# TEXTO ABAIXO DO MAPA
# =====================
st.markdown("""
Cada ponto representa **uma presença consciente**.  
A localização é **aproximada**, com espalhamento visual para preservar privacidade.

🌱 Movimento da Paz Viva  
📍 Distribuição simbólica global
""")
