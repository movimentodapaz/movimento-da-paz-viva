import instaloader
import sqlite3
import re
from datetime import datetime
from pathlib import Path
from geopy.geocoders import Nominatim
import time

# =========================
# CONFIG
# =========================

INSTAGRAM_USER = "dapazmovimento"  # conta pública
DB_PATH = Path("data/pacificadores.db")

# =========================
# DB
# =========================

def get_conn():
    return sqlite3.connect(DB_PATH)

def inserir_pacificador(cidade, pais, lat, lon):
    conn = get_conn()
    conn.execute("""
        INSERT INTO pacificadores
        (cidade, pais, latitude, longitude, data_registro)
        VALUES (?, ?, ?, ?, ?)
    """, (cidade, pais, lat, lon, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

# =========================
# GEO
# =========================

geolocator = Nominatim(user_agent="movimento-paz-viva")

def geocodificar(local):
    try:
        location = geolocator.geocode(local, timeout=10)
        if location:
            return location.latitude, location.longitude
    except:
        pass
    return None, None

# =========================
# BIO PARSER SIMPLES
# =========================

def extrair_local(bio):
    if not bio:
        return None
    # exemplos simples: "São Paulo - Brasil", "Lisboa 🇵🇹"
    m = re.search(r"([A-Za-zÀ-ÿ\s]+)", bio)
    return m.group(1).strip() if m else None

# =========================
# MAIN
# =========================

L = instaloader.Instaloader(download_pictures=False, download_videos=False)

profile = instaloader.Profile.from_username(L.context, INSTAGRAM_USER)

for follower in profile.get_followers():
    bio = follower.biography
    local = extrair_local(bio)

    if local:
        lat, lon = geocodificar(local)
        if lat and lon:
            inserir_pacificador(
                cidade=local,
                pais="Desconhecido",
                lat=lat,
                lon=lon
            )
            time.sleep(2)  # evita bloqueio

print("Coleta concluída.")
