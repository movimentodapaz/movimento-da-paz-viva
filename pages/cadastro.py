import streamlit as st
import sqlite3
from pathlib import Path
import hashlib
from datetime import datetime

from locales import pt, en, es, fr, zh, ru, ar


st.set_page_config(
    page_title="Cadastro",
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

def get_device_id():
    raw = st.session_state.get("client_id", "device")
    return hashlib.sha256(raw.encode()).hexdigest()

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
st.markdown(f"## {T['register_title']}")
st.markdown(f"<p>{T['register_intro']}</p>", unsafe_allow_html=True)

with st.form("cadastro"):
    nome = st.text_input(T["field_name"])
    email = st.text_input(T["field_email"])
    cidade = st.text_input(T["field_city"])
    pais = st.text_input(T["field_country"])
    enviar = st.form_submit_button(T["submit"])

if enviar:
    conn = get_conn()
    cur = conn.cursor()
    device_id = get_device_id()

    cur.execute("SELECT 1 FROM pacificadores WHERE device_id = ?", (device_id,))
    if cur.fetchone():
        st.warning(T["already_registered"])
    else:
        cur.execute("""
            INSERT INTO pacificadores
            (nome, email, cidade, pais, latitude, longitude, device_id, data_registro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            nome, email, cidade, pais,
            0.0, 0.0,
            device_id,
            datetime.utcnow().isoformat()
        ))
        conn.commit()
        st.success(T["success"])

st.divider()

# ---------- BOTÃO VOLTAR ----------
if st.button("⬅️ Home", use_container_width=True):
    st.switch_page("streamlit_app.py")
