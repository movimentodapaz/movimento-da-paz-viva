import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from pathlib import Path
import random

DB_PATH = Path("data/pacificadores.db")

def render_mapa():
    def get_conn():
        return sqlite3.connect(DB_PATH)

    df = pd.read_sql("SELECT * FROM pacificadores", get_conn())

    if df.empty:
        st.info("Ainda não há pacificadores registrados.")
        return

    def jitter(lat, lon, radius_m=1200):
        r = radius_m / 111_000
        return lat + random.uniform(-r, r), lon + random.uniform(-r, r)

    df["lat_plot"], df["lon_plot"] = zip(*df.apply(
        lambda r: jitter(r.latitude, r.longitude), axis=1
    ))

    fig = px.scatter_mapbox(
        df,
        lat="lat_plot",
        lon="lon_plot",
        mapbox_style="open-street-map",
        zoom=1.4,
        center=dict(lat=-14.2, lon=-51.9),
        opacity=0.65,
        height=720
    )

    fig.update_traces(
        marker=dict(size=10, color="rgba(0,200,255,0.85)"),
        hoverinfo="skip"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "scrollZoom": True,
            "displayModeBar": True,
            "displaylogo": False
        }
    )
