import streamlit as st
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime

# ---------- IDIOMA ----------
T = st.session_state.get("texts")
if T is None:
    st.error("Idioma não carregado.")
    st.stop()

st.set_page_config(
    page_title=T["nav_register"],
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- DEVICE ID (ESTÁVEL E SIMPLES) ----------
if "device_id" not in st.session_state:
    st.session_state["device_id"] = str(uuid.uuid4())

device_id = st.session_state["device_id"]

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

# ---------- GEO (TEMPORÁRIO) ----------
def geocode_stub(cidade, pais):
    if pais.lower() == "brasil":
        return -14.2350, -51.9253
    return 0.0, 0.0

# ---------- UI ----------
st.markdown(f"## {T['register_title']}")
st.markdown(T["register_intro"], unsafe_allow_html=True)

nome = st.text_input(T["field_name"])
email = st.text_input(T["field_email"])
cidade = st.text_input(T["field_city"])
pais = st.text_input(T["field_country"])

if st.button(T["submit"], use_container_width=True):
    if not cidade or not pais:
        st.warning("Cidade e país são obrigatórios.")
    else:
        lat, lon = geocode_stub(cidade, pais)
        agora = datetime.utcnow().isoformat()

        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            "SELECT id FROM pacificadores WHERE device_id = ?",
            (device_id,)
        )
        existe = cur.fetchone()

        if existe:
            cur.execute("""
                UPDATE pacificadores
                SET nome = ?, email = ?, cidade = ?, pais = ?,
                    latitude = ?, longitude = ?, data_registro = ?
                WHERE device_id = ?
            """, (
                nome, email, cidade, pais,
                lat, lon, agora, device_id
            ))
            conn.commit()
            st.success("🌞 Sua presença foi atualizada com sucesso.")
        else:
            cur.execute("""
                INSERT INTO pacificadores
                (nome, email, cidade, pais, latitude, longitude, device_id, data_registro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                nome, email, cidade, pais,
                lat, lon, device_id, agora
            ))
            conn.commit()
            st.success(T["success"])

        conn.close()

st.divider()

if st.button("⬅️ Home", use_container_width=True):
    st.switch_page("streamlit_app.py")
