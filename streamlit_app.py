import streamlit as st
from components.mapa import render_mapa
import streamlit.components.v1 as components
import base64
from pathlib import Path

from locales import pt, en


st.set_page_config(
    page_title="Home",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- CSS: ESCONDE MENU E HEADER PADRÃO ----------
st.markdown("""
<style>
[data-testid="stSidebar"] {
    display: none;
}
[data-testid="stHeader"] {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# ---------- SELETOR DE IDIOMA ----------
LANGS = {
    "pt": pt.TEXTS,
    "en": en.TEXTS,
}

lang = st.selectbox(
    "🌐 Language / Idioma",
    options=list(LANGS.keys()),
    format_func=lambda x: LANGS[x]["lang_name"],
    index=0
)

T = LANGS[lang]

# ---------- LOGO EM BASE64 ----------
BASE_DIR = Path(__file__).resolve().parent
logo_path = BASE_DIR / "assets" / "logo_paz.png"

with open(logo_path, "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode("utf-8")

# ---------- NAVEGAÇÃO POR BOTÕES ----------
nav1, nav2, nav3 = st.columns(3)

with nav1:
    st.button(f"🏠 {T['nav_home']}", use_container_width=True)

with nav2:
    if st.button(f"📝 {T['nav_register']}", use_container_width=True):
        st.switch_page("pages/cadastro.py")

with nav3:
    if st.button(f"🌍 {T['nav_map']}", use_container_width=True):
        st.switch_page("pages/pacificadores.py")

st.divider()

# ---------- TOPO ----------
col1, col2, col3 = st.columns([1.2, 3.6, 1.2])

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
            0% {{ transform: rotate(0deg) scale(0.95); }}
            50% {{ transform: rotate(180deg) scale(1.05); }}
            100% {{ transform: rotate(360deg) scale(0.95); }}
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

with col2:
    st.markdown(
        f"""
        <h1 style="text-align:center; margin-top:40px">
            {T["title"]}
        </h1>
        <p style="text-align:center; font-size:18px; max-width:900px; margin:auto">
            {T["subtitle"]}
        </p>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown("<div style='height:70px'></div>", unsafe_allow_html=True)
    if st.button(f"🌍 {T['cta']}", use_container_width=True):
        st.switch_page("pages/cadastro.py")

st.divider()

# ---------- MAPA ----------
st.markdown(f"## {T['map_title']}")
render_mapa()
