import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl
from jinja2 import Template

# Brug hele siden
st.set_page_config(layout="wide")

# --- Hent data ---
SHEET_ID = "1DNHbwKxJ9_HKLtfJ_hC0jeHnKlmana_thEBQfr2sMfM"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
data = pd.read_csv(url)

# Konverter lat/lon (hvis komma som decimal)
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
ansager_lat, ansager_lon = 55.703423, 8.755025
m = folium.Map(location=[ansager_lat, ansager_lon], zoom_start=15)

# Tilføj "Find mig"-knap
LocateControl(auto_start=False).add_to(m)

# --- Indsæt JavaScript direkte for flydende live-position ---
js_code = Template("""
<script>
if (navigator.geolocation) {
    navigator.geolocation.watchPosition(function(pos) {
        var lat = pos.coords.latitude;
        var lon = pos.coords.longitude;
        if (!window.userMarker) {
            window.userMarker = L.marker([lat, lon]).addTo({{map_name}});
            window.userMarker.bindPopup("📍 Du er her!").openPopup();
            {{map_name}}.setView([lat, lon], 17);
        } else {
            window.userMarker.setLatLng([lat, lon]);
        }
    },
    function(err){ console.log(err); },
    { enableHighAccuracy: true, maximumAge: 5000, timeout: 10000 });
}
</script>
""").render(map_name=m.get_name())

m.get_root().html.add_child(folium.Element(js_code))

# --- Tilføj prikker ---
for _, row in data.iterrows():
    farve = 'green' if row['betalt'] == 1 else 'red'

    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=9,
        color=None,
        fill=True,
        fill_color=farve,
        fill_opacity=0.4
    ).add_to(m)

    adresse = row['adresse']
    husnummer = adresse.split(',')[0].split()[-1]

    folium.map.Marker(
        [row['lat'], row['lon']],
        icon=folium.DivIcon(
            html=f"""<div style="font-size:10px; color:black">{husnummer}</div>"""
        )
    ).add_to(m)

# --- Vis kort ---
st_folium(m, width=None, height=800)
