import streamlit as st
import sqlite3
from pathlib import Path
import hashlib
from datetime import datetime

from locales import pt, en


st.set_page_config(
    page_title="Cadastro",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- IDIOMAS ----------
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

# ---------- RESOLUÇÃO DE PATH ----------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "pacificadores.db"


# ---------- FUNÇÕES ----------
def get_device_id():
    raw = f"{st.session_state.get('client_id', '')}{st.session_state.get('browser', '')}"
    return hashlib.sha256(raw.encode()).hexdigest()


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


# ---------- INTERFACE ----------
st.markdown(f"## {T['register_title']}")
st.markdown(
    f"<p style='font-size:16px'>{T['register_intro']}</p>",
    unsafe_allow_html=True
)

with st.form("cadastro_form"):
    nome = st.text_input(T["field_name"])
    email = st.text_input(T["field_email"])
    cidade = st.text_input(T["field_city"])
    pais = st.text_input(T["field_country"])

    submitted = st.form_submit_button(T["submit"])

    if submitted:
        device_id = get_device_id()
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM pacificadores WHERE device_id = ?",
            (device_id,)
        )

        if cursor.fetchone():
            st.warning(T["already_registered"])
        else:
            # Latitude/Longitude fictícias (mantém lógica atual)
            latitude = 0.0
            longitude = 0.0

            cursor.execute("""
                INSERT INTO pacificadores (
                    nome, email, cidade, pais,
                    latitude, longitude,
                    device_id, data_registro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                nome,
                email,
                cidade,
                pais,
                latitude,
                longitude,
                device_id,
                datetime.utcnow().isoformat()
            ))

            conn.commit()
            st.success(T["success"])
