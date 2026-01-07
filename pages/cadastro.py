import streamlit as st
import sqlite3
from pathlib import Path
from datetime import datetime
import requests
import uuid
import time

# =====================
# CONFIG
# =====================
st.set_page_config(
    page_title="Cadastro de Pacificador",
    layout="centered"
)

DB_PATH = Path("data/pacificadores.db")
DB_PATH.parent.mkdir(exist_ok=True)

# =====================
# DEVICE ID (1 por aparelho)
# =====================
if "device_id" not in st.session_state:
    st.session_state.device_id = str(uuid.uuid4())

DEVICE_ID = st.session_state.device_id

# =====================
# DB
# =====================
def get_conn():
    return sqlite3.connect(DB_PATH)

def column_exists(conn, table, column):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cur.fetchall()]
    return column in cols

def ensure_db():
    conn = get_conn()
    cur = conn.cursor()

    # Cria tabela base (caso não exista)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pacificadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cidade TEXT,
            pais TEXT,
            latitude REAL,
            longitude REAL,
            data_registro TEXT
        )
    """)

    # Migra colunas novas com segurança
    if not column_exists(conn, "pacificadores", "nome"):
        cur.execute("ALTER TABLE pacificadores ADD COLUMN nome TEXT")

    if not column_exists(conn, "pacificadores", "email"):
        cur.execute("ALTER TABLE pacificadores ADD COLUMN email TEXT")

    if not column_exists(conn, "pacificadores", "device_id"):
        cur.execute("ALTER TABLE pacificadores ADD COLUMN device_id TEXT")

    conn.commit()
    conn.close()

ensure_db()

# =====================
# GEOLOCALIZAÇÃO
# =====================
def geocode_city(cidade, pais):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "city": cidade,
            "country": pais,
            "format": "json",
            "limit": 1
        }
        headers = {"User-Agent": "MovimentoPazViva/1.0"}
        r = requests.get(url, params=params, headers=headers, timeout=10)
        data = r.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except:
        pass
    return None, None

# =====================
# VERIFICA DUPLICIDADE
# =====================
def device_ja_cadastrado(device_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM pacificadores WHERE device_id = ?",
        (device_id,)
    )
    existe = cur.fetchone() is not None
    conn.close()
    return existe

# =====================
# INTERFACE
# =====================
st.title("🌿 Torne-se um Pacificador no Movimento da Paz Viva")

st.markdown("""
O Movimento da Paz Viva é um campo coletivo de presença consciente.

Ao se registrar, você **não entra em uma rede social** —  
você passa a **sustentar simbolicamente a paz interior**  
e permite que essa presença seja visível no mapa do mundo.

Cada ponto representa **uma consciência em silêncio**.
""")

st.divider()

# =====================
# BLOQUEIO DE DUPLICIDADE
# =====================
if device_ja_cadastrado(DEVICE_ID):
    st.info(
        "✨ Este aparelho já registrou uma presença no Movimento da Paz Viva.\n\n"
        "Seja bem-vindo novamente ao campo."
    )
    st.stop()

# =====================
# FORMULÁRIO
# =====================
with st.form("cadastro_pacificador", clear_on_submit=True):
    nome = st.text_input("Nome ou apelido (opcional)")
    email = st.text_input("E-mail (opcional)")

    cidade = st.text_input("Cidade *")
    pais = st.text_input("País *")

    consentimento = st.checkbox(
        "Declaro que participo voluntariamente do Movimento da Paz Viva."
    )

    enviar = st.form_submit_button("🌍 Registrar minha presença")

# =====================
# SUBMISSÃO
# =====================
if enviar:
    if not cidade or not pais or not consentimento:
        st.warning("Por favor, preencha os campos obrigatórios.")
    else:
        with st.spinner("Registrando sua presença no mapa..."):
            lat, lon = geocode_city(cidade, pais)
            time.sleep(1)

        if lat is None:
            st.error("Não foi possível localizar essa cidade. Tente outra forma de escrita.")
        else:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO pacificadores
                (nome, email, cidade, pais, latitude, longitude, device_id, data_registro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    nome.strip() if nome else None,
                    email.strip().lower() if email else None,
                    cidade.strip(),
                    pais.strip(),
                    lat,
                    lon,
                    DEVICE_ID,
                    datetime.utcnow().isoformat()
                )
            )
            conn.commit()
            conn.close()

            st.success("✨ Sua presença foi registrada com sucesso!")
            st.markdown(
                "Você já pode ver seu ponto no **Mapa dos Pacificadores**."
            )
