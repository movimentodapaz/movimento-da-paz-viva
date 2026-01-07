import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from pathlib import Path
import random

# =====================
# CONFIGURAÇÃO DA PÁGINA
# =====================
st.set_page_config(
    page_title="Mapa dos Pacificadores – Movimento da Paz Viva",
    layout="wide"
)

# =====================
# CAMINHO DO BANCO
# =====================
DB_PATH = Path("data/pacificadores.db")

# =====================
# CONEXÃO COM BANCO
# =====================
def get_conn():
    return sqlite3.connect(DB_PATH)

def load_data():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM pacificadores", conn)
    conn.close()
    return df

df = load_data()

# =====================
# CONTADORES (ROBUSTOS)
# =====================
total = len(df)

def is_brasil(pais):
    if not isinstance(pais, str):
        return False
    pais = pais.lower()
    return any(x in pais for x in ["brasil", "brazil", "br"])

brasil = df["pais"].apply(is_brasil).sum() if not df.empty else 0
exterior = total - brasil

# =====================
# HEADER
# =====================
st.markdown(
    "<h1 style='margin-top:-50px'>🌍 Mapa dos Pacificadores da Paz Viva</h1>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <p style="font-size:16px; max-width:900px;">
    O <strong>Movimento da Paz Viva</strong> é uma iniciativa independente e global.
    Cada ponto neste mapa representa uma pessoa real que escolheu sustentar a paz interior
    como prática consciente, contribuindo silenciosamente para a transformação coletiva.
    </p>
    """,
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)
col1.metric("🌍 Pacificadores", total)
col2.metric("🇧🇷 Brasil", brasil)
col3.metric("🌐 Exterior", exterior)

st.divider()

# =====================
# FUNÇÃO DE ESPALHAMENTO (JITTER)
# =====================
def jitter(lat, lon, radius_m=1500):
    r = radius_m / 111_000
    return (
        lat + random.uniform(-r, r),
        lon + random.uniform(-r, r)
    )

# =====================
# MAPA
# =====================
if df.empty:
    st.info("Ainda não há pacificadores registrados.")
else:
    # Aplica espalhamento visual
    df["lat_plot"], df["lon_plot"] = zip(*df.apply(
        lambda r: jitter(r.latitude, r.longitude),
        axis=1
    ))

    fig = px.density_mapbox(
        df,
        lat="lat_plot",
        lon="lon_plot",
        radius=12,
        center=dict(lat=-14.2, lon=-51.9),
        zoom=1.4,
        mapbox_style="open-street-map",  # visual mais Google Maps-like
        opacity=0.85
    )

    fig.update_layout(
        height=720,
        margin=dict(l=0, r=0, t=0, b=0),
        mapbox=dict(
            bearing=0,
            pitch=0
        )
    )

    # IMPORTANTE:
    # scrollZoom e controles ficam no CONFIG do Streamlit,
    # NÃO no layout do Plotly
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "scrollZoom": True,      # zoom com scroll do mouse
            "displayModeBar": True, # barra de ferramentas visível
            "displaylogo": False,
            "modeBarButtonsToAdd": [
                "zoomInMapbox",
                "zoomOutMapbox",
                "resetViewMapbox"
            ]
        }
    )

# =====================
# TEXTO INSTITUCIONAL
# =====================
st.markdown("""
Cada ponto representa **uma presença consciente**.  
A localização é **aproximada**, com espalhamento visual para preservar privacidade.

🌱 **Movimento da Paz Viva**  
📍 Distribuição simbólica global
""")
