import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.graph_objects as go

# ---------- CONFIG ----------
st.set_page_config(
    page_title="Mapa dos Pacificadores",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- IDIOMA ----------
T = st.session_state.get("texts", {
    "map_title": "Mapa dos Pacificadores",
    "empty_map": "Nenhum pacificador registrado."
})

# ---------- PATH BANCO ----------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "pacificadores.db"

def get_conn():
    DATA_DIR.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)

# ---------- TÍTULO ----------
st.markdown(f"## {T['map_title']}")

# ---------- DADOS ----------
df = pd.read_sql("SELECT * FROM pacificadores", get_conn())

if df.empty:
    st.info(T["empty_map"])
else:
    # ---------- CONTADORES ----------
    total = len(df)
    brasil = len(df[df["pais"].str.lower().str.contains("brasil")])
    exterior = total - brasil

    c1, c2, c3 = st.columns(3)
    c1.metric("🌍 Total", total)
    c2.metric("🇧🇷 Brasil", brasil)
    c3.metric("🌎 Exterior", exterior)

    # ---------- VALIDA COORDENADAS ----------
    df = df[
        df["latitude"].between(-90, 90) &
        df["longitude"].between(-180, 180)
    ]

    # ---------- JITTER LEVE ----------
    jitter = 0.001
    lat = df["latitude"] + np.random.uniform(-jitter, jitter, len(df))
    lon = df["longitude"] + np.random.uniform(-jitter, jitter, len(df))

    # ---------- MAPA ----------
    fig = go.Figure(
        go.Scattermapbox(
            lat=lat,
            lon=lon,
            mode="markers",
            marker=dict(
                size=10,
                color="#FFD700",  # dourado
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

    # ✅ SCROLL DO MOUSE ATIVADO AQUI
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"scrollZoom": True}
    )

st.divider()

# ---------- BOTÃO VOLTAR ----------
if st.button("⬅️ Home", use_container_width=True):
    st.switch_page("streamlit_app.py")
