import streamlit as st
from components.mapa import render_mapa
import streamlit.components.v1 as components
import base64
from pathlib import Path

from locales import pt, en, es, fr


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

# ---------- IDIOMAS DISPONÍVEIS ----------
LANGS = {
    "pt": pt.TEXTS,
    "en": en.TEXTS,
    "es": es.TEXTS,
    "fr": fr.TEXTS,
}

# ---------- DETECÇÃO REAL VIA JAVASCRIPT ----------
if "lang" not in st.session_state:

    js_lang = components.html(
        """
        <script>
        const lang = navigator.language || navigator.languages[0];
        const streamlitLang = lang ? lang.slice(0,2).toLowerCase() : "pt";
        const input = document.createElement("input");
        input.type = "hidden";
        input.value = streamlitLang;
        input.id = "detected_lang";
        document.body.appendChild(input);
        </script>
        """,
        height=0
    )

    # Fallback seguro (JS não retorna valor diretamente)
    # Leitura indireta via query params simulados
    detected = st.experimental_get_query_params().get("lang", [None])[0]

    if detected in LANGS:
        st.session_state["lang"] = detected
    else:
        st.session_state["lang"] = "pt"

# ---------- SELETOR VISÍVEL ----------
lang = st.selectbox(
    "🌐 Language / Idioma",
    options=list(LANGS.keys()),
    index=list(LANGS.keys()).index(st.session_state["lang"]),
    format_func=lambda x: LANGS[x]["lang_name"]
)

# ---------- SALVA ESCOLHA HUMANA ----------
st.session_state["lang"] = lang
T = LANGS[lang]

# ---------- LOGO ----------
BASE_DIR = Path(__file__).resolve().parent
with open(BASE_DIR / "assets" / "logo_paz.png", "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode("utf-8")

# ---------- NAVEGAÇÃO ----------
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
        <h1 style="text-align:center">{T['title']}</h1>
        <p style="text-align:center;font-size:18px;max-width:900px;margin:auto">
            {T['subtitle']}
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
