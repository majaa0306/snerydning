import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

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

# Tilføj prikker
for _, row in data.iterrows():
    farve = 'green' if row['betalt'] == 1 else 'red'
    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=4,
        color=farve,
        fill=True,
        fill_color=farve,
        fill_opacity=0.7,
        popup=row['adresse']
    ).add_to(m)

# Tilføj legend
legend_html = '''
<div style="position: fixed; bottom: 50px; left: 50px; width: 150px; height: 70px; border:2px solid grey; z-index:9999; font-size:14px; background-color:white; padding: 10px;">
<b>Betaling:</b><br>
<i style="color:green;">●</i> Betalt<br>
<i style="color:red;">●</i> Ikke betalt
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Vis kort
st_folium(m, width=1000, height=700)
