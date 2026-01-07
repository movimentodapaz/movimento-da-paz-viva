import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(
    r"C:\pazenv\movimento-da-paz-viva\data\pacificadores.db"
)

pacificadores = [
    ("São Paulo", "Brasil", -23.5505, -46.6333),
    ("Rio de Janeiro", "Brasil", -22.9068, -43.1729),
    ("Lisboa", "Portugal", 38.7169, -9.1399),
    ("Madrid", "Espanha", 40.4168, -3.7038),
    ("Buenos Aires", "Argentina", -34.6037, -58.3816),
]

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

for cidade, pais, lat, lon in pacificadores:
    cur.execute("""
        INSERT INTO pacificadores
        (cidade, pais, latitude, longitude, data_registro)
        VALUES (?, ?, ?, ?, ?)
    """, (cidade, pais, lat, lon, datetime.utcnow().isoformat()))

conn.commit()
conn.close()

print("Pacificadores inseridos com sucesso.")
