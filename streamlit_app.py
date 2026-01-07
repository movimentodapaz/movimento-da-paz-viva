import streamlit as st
from components.mapa import render_mapa
import streamlit.components.v1 as components
import base64
from pathlib import Path

st.set_page_config(
    page_title="Movimento da Paz Viva",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- RESOLUÇÃO SEGURA DE PATH ----------
BASE_DIR = Path(__file__).resolve().parent
logo_path = BASE_DIR / "assets" / "logo_paz.png"

if not logo_path.exists():
    st.error(f"Logo não encontrado em: {logo_path}")
    st.stop()

# ---------- CARREGA LOGO EM BASE64 ----------
with open(logo_path, "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode("utf-8")

# ---------- TOPO EM 3 COLUNAS ----------
col1, col2, col3 = st.columns([1.2, 3.6, 1.2])

# COLUNA 1 — LOGO ANIMADO NATIVO
with col1:
    components.html(
        f"""
        <html>
        <head>
        <style>
        body {{
            margin: 0;
            height: 220px;
            display: flex;
            justify-content: center;
            align-items: center;
            background: transparent;
        }}

        img {{
            width: 130px;
            animation: respirar 12s ease-in-out infinite;
            opacity: 0.95;
        }}

        @keyframes respirar {{
            0% {{
                transform: rotate(0deg) scale(0.95);
            }}
            50% {{
                transform: rotate(180deg) scale(1.05);
            }}
            100% {{
                transform: rotate(360deg) scale(0.95);
            }}
        }}
        </style>
        </head>
        <body>
            <img src="data:image/png;base64,{logo_base64}">
        </body>
        </html>
        """,
        height=220,
    )

# COLUNA 2 — TÍTULO E TEXTO
with col2:
    st.markdown("""
    <h1 style="text-align:center; margin-top:40px">
        Movimento da Paz Viva
    </h1>
    <p style="text-align:center; font-size:18px; max-width:900px; margin:auto">
        Um campo coletivo de presença consciente.<br>
        Pessoas reais, espalhadas pelo mundo, sustentando a paz interior como prática viva.
    </p>
    """, unsafe_allow_html=True)

# COLUNA 3 — BOTÃO
with col3:
    st.markdown("<div style='height:70px'></div>", unsafe_allow_html=True)
    if st.button("🌍 Tornar-me um Pacificador", use_container_width=True):
        st.switch_page("pages/cadastro.py")

st.divider()

# ---------- MAPA ----------
st.markdown("## 🌐 Presença Global em Tempo Real")
render_mapa()
