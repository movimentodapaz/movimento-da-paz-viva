import streamlit as st
import sqlite3
import requests
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
            data_registro TEXT
        )
    """)
    conn.commit()
    return conn

# ---------- GEOCODIFICAÇÃO REAL ----------
def geocode_city(cidade, pais):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": f"{cidade}, {pais}",
            "format": "json",
            "limit": 1
        }
        headers = {"User-Agent": "MovimentoPazViva/1.0"}
        r = requests.get(url, params=params, headers=headers, timeout=10)
        data = r.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None, None

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
        lat, lon = geocode_city(cidade, pais)
        if lat is None or lon is None:
            st.error("Não foi possível localizar a cidade informada.")
            st.stop()

        agora = datetime.utcnow().isoformat()
        conn = get_conn()
        cur = conn.cursor()

        # ---------- CRITÉRIO DE ATUALIZAÇÃO ----------
        if email:
            cur.execute(
                "SELECT id FROM pacificadores WHERE email = ?",
                (email,)
            )
        else:
            cur.execute(
                "SELECT id FROM pacificadores WHERE nome = ? AND cidade = ? AND pais = ?",
                (nome, cidade, pais)
            )

        existe = cur.fetchone()

        if existe:
            cur.execute("""
                UPDATE pacificadores
                SET nome = ?, email = ?, cidade = ?, pais = ?,
                    latitude = ?, longitude = ?, data_registro = ?
                WHERE id = ?
            """, (
                nome, email, cidade, pais,
                lat, lon, agora, existe[0]
            ))
            conn.commit()
            st.success("🌞 Sua presença foi atualizada com sucesso.")
        else:
            cur.execute("""
                INSERT INTO pacificadores
                (nome, email, cidade, pais, latitude, longitude, data_registro)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                nome, email, cidade, pais,
                lat, lon, agora
            ))
            conn.commit()
            st.success(T["success"])

        conn.close()

st.divider()

if st.button("⬅️ Home", use_container_width=True):
    st.switch_page("streamlit_app.py")
