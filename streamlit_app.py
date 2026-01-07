# -*- coding: utf-8 -*-

import streamlit as st
from components.mapa import render_mapa
import streamlit.components.v1 as components
import base64
from pathlib import Path
import importlib


st.set_page_config(
    page_title="Home",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- CSS ----------
st.markdown("""
<style>
[data-testid="stSidebar"] { display: none; }
[data-testid="stHeader"] { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ---------- CARREGAMENTO DINÂMICO DE IDIOMAS ----------
AVAILABLE_LANGS = ["pt", "en", "es", "fr", "zh", "ru", "ar"]
LANGS = {}

for code in AVAILABLE_LANGS:
    try:
        module = importlib.import_module(f"locales.{code}")
        LANGS[code] = module.TEXTS
    except Exception:
        # Se um idioma falhar, ele simplesmente não entra
        pass

# Fallback absoluto
if "pt" not in LANGS:
    LANGS["pt"] = {
        "lang_name": "Português",
        "title": "Movimento da Paz Viva",
        "subtitle": "Um campo coletivo de presença consciente.",
        "cta": "Tornar-me um Pacificador",
        "map_title": "🌐 Presença Global",
        "nav_home": "Home",
        "nav_register": "Cadastro",
        "nav_map": "Mapa",
        "credit": "Fundado em 1º de Dezembro de 2025 por José Carlos Rosa Farias"
    }

# ---------- IDIOMA ATIVO ----------
if "lang" not in st.session_state or st.session_state["lang"] not in LANGS:
    st.session_state["lang"] = "pt"

lang = st.selectbox(
    "🌐 Language / Idioma",
    options=list(LANGS.keys()),
    index=list(LANGS.keys()).index(st.session_state["lang"]),
    format_func=lambda x: LANGS[x].get("lang_name", x)
)

st.session_state["lang"] = lang
T = LANGS[lang]

# Disponibiliza textos globalmente
st.session_state["texts"] = T


# ---------- LOGO ----------
BASE_DIR = Path(__file__).resolve().parent
logo_path = BASE_DIR / "assets" / "logo_paz.png"

if logo_path.exists():
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode("utf-8")
else:
    logo_base64 = ""


# ---------- NAVEGAÇÃO ----------
nav1, nav2, nav3 = st.columns(3)

with nav1:
    st.button(f"🏠 {T.get('nav_home', 'Home')}", use_container_width=True)

with nav2:
    if st.button(f"📝 {T.get('nav_register', 'Cadastro')}", use_container_width=True):
        st.switch_page("pages/cadastro.py")

with nav3:
    if st.button(f"🌍 {T.get('nav_map', 'Mapa')}", use_container_width=True):
        st.switch_page("pages/pacificadores.py")

st.divider()


# ---------- TOPO ----------
col1, col2, col3 = st.columns([1.2, 3.6, 1.2])

with col1:
    if logo_base64:
        components.html(
            f"""
            <html><body style="margin:0;height:220px;display:flex;align-items:center;justify-content:center;">
            <img src="data:image/png;base64,{logo_base64}" style="width:130px;animation:spin 12s ease-in-out infinite;">
            <style>
            @keyframes spin {{
                0% {{ transform: rotate(0deg) scale(.95); }}
                50% {{ transform: rotate(180deg) scale(1.05); }}
                100% {{ transform: rotate(360deg) scale(.95); }}
            }}
            </style>
            </body></html>
            """,
            height=220
        )

with col2:
    st.markdown(
        f"""
        <h1 style="text-align:center">{T.get('title','')}</h1>
        <p style="text-align:center;font-size:18px;max-width:900px;margin:auto">
            {T.get('subtitle','')}
        </p>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown("<div style='height:70px'></div>", unsafe_allow_html=True)
    if st.button(f"🌍 {T.get('cta','')}", use_container_width=True):
        st.switch_page("pages/cadastro.py")

st.divider()


# ---------- MAPA ----------
st.markdown(f"## {T.get('map_title','')}")
render_mapa()

st.divider()


# ---------- CRÉDITO ----------
st.markdown(
    f"""
    <p style="text-align:center; font-size:14px; opacity:0.7; margin-top:40px">
    {T.get('credit','')}
    </p>
    """,
    unsafe_allow_html=True
)
