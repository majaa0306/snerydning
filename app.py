import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

# Brug hele siden
st.set_page_config(layout="wide")

# Google Sheet ID
SHEET_ID = "1DNHbwKxJ9_HKLtfJ_hC0jeHnKlmana_thEBQfr2sMfM"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# Læs data direkte fra Google Sheets
data = pd.read_csv(url)

# Hvis lat/lon bruger komma som decimal, konverter til punktum
data['lat'] = data['lat'].astype(str).str.replace(',', '.').astype(float)
data['lon'] = data['lon'].astype(str).str.replace(',', '.').astype(float)

# --- Filtreringsmuligheder ---
status_valg = st.sidebar.selectbox("Vis:", ["Alle", "Kun betalt", "Kun ikke-betalt"])
if status_valg == "Kun betalt":
    data = data[data['betalt'] == 1]
elif status_valg == "Kun ikke-betalt":
    data = data[data['betalt'] == 0]

gader = ["Alle"] + sorted(data['adresse'].apply(lambda x: x.split()[0]).unique())
gade_valg = st.sidebar.selectbox("Vælg gade:", gader)
if gade_valg != "Alle":
    data = data[data['adresse'].str.startswith(gade_valg)]

# --- Opret Folium-kort ---
ansager_lat = 55.703423
ansager_lon = 8.755025
m = folium.Map(location=[ansager_lat, ansager_lon], zoom_start=15)

# Tilføj prikker med kun husnummer
for _, row in data.iterrows():
    farve = 'green' if row['betalt'] == 1 else 'red'
    
    # Selve prikken
    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=9,
        color=None,
        fill=True,
        fill_color=farve,
        fill_opacity=0.4
    ).add_to(m)
    
    # Træk husnummer ud
    husnummer = row['adresse'].split()[1]  
    
    # Tekst ved siden af prikken
    folium.map.Marker(
        [row['lat'], row['lon']],
        icon=folium.DivIcon(
            html=f"""<div style="font-size:10px; color:black">{husnummer}</div>"""
        )
    ).add_to(m)

# Vis kort i fuld bredde
st_folium(m, width=None, height=800)
