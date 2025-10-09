import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl
from folium import MacroElement
from jinja2 import Template

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
@st.cache_resource
def init_map():
    m = folium.Map(location=[55.703423, 8.755025], zoom_start=15)
    LocateControl(auto_start=False).add_to(m)
    m.get_root().add_child(LocateOnLoad())
    return m

m = init_map()


# Tilføj "Find mig"-knap
LocateControl(auto_start=False).add_to(m)

# --- Automatisk centrering på brugerens position ---
class LocateOnLoad(MacroElement):
    def __init__(self):
        super().__init__()
        self._template = Template("""
            {% macro script(this, kwargs) %}
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(pos) {
                    var lat = pos.coords.latitude;
                    var lon = pos.coords.longitude;
                    {{this._parent.get_name()}}.setView([lat, lon], 17);
                    L.marker([lat, lon]).addTo({{this._parent.get_name()}})
                        .bindPopup("📍 Du er her!").openPopup();
                });
            }
            {% endmacro %}
        """)

# Tilføj automatisk positionering
m.get_root().add_child(LocateOnLoad())

# --- Tilføj prikker for adresser ---
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
    
    # Træk husnummer ud som sidste ord før komma
    adresse = row['adresse']
    husnummer = adresse.split(',')[0].split()[-1]  # sidste ord i første del af adressen

    # Tekst ved siden af prikken
    folium.map.Marker(
        [row['lat'], row['lon']],
        icon=folium.DivIcon(
            html=f"""<div style="font-size:10px; color:black">{husnummer}</div>"""
        )
    ).add_to(m)

# --- Vis kort i fuld bredde ---
st_folium(m, width=None, height=800)
