import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# --- Hent data fra Google Sheets ---
SHEET_ID = "1DNHbwKxJ9_HKLtfJ_hC0jeHnKlmana_thEBQfr2sMfM"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
data = pd.read_csv(url)

# Sørg for korrekte koordinater
data['lat'] = data['lat'].astype(str).str.replace(',', '.').astype(float)
data['lon'] = data['lon'].astype(str).str.replace(',', '.').astype(float)

# --- Sidebar filtrering ---
status_valg = st.sidebar.selectbox("Vis:", ["Alle", "Kun betalt", "Kun ikke-betalt"])
if status_valg == "Kun betalt":
    data = data[data['betalt'] == 1]
elif status_valg == "Kun ikke-betalt":
    data = data[data['betalt'] == 0]

gader = ["Alle"] + sorted(data['adresse'].apply(lambda x: x.split()[0]).unique())
gade_valg = st.sidebar.selectbox("Vælg gade:", gader)
if gade_valg != "Alle":
    data = data[data['adresse'].str.startswith(gade_valg)]

# --- Lav JSON til JavaScript ---
json_data = data.to_dict(orient="records")

# --- Indlejret Leaflet-kort ---
st.components.v1.html(f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link
  rel="stylesheet"
  href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  #map {{
    height: 90vh;
    width: 100%;
    border-radius: 10px;
  }}
</style>
</head>
<body>
<div id="map"></div>
<script>
var map = L.map('map').setView([55.703423, 8.755025], 15);

// OpenStreetMap lag
L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
  maxZoom: 19,
}}).addTo(map);

// Data fra Python
var points = {json_data};

// Tilføj røde/grønne prikker (uden numre)
points.forEach(p => {{
  var color = p.betalt == 1 ? 'green' : 'red';
  L.circleMarker([p.lat, p.lon], {{
    radius: 8,
    color: color,
    fillOpacity: 0
  }}).addTo(map);
}});

// Live GPS tracking + map følger position
if (navigator.geolocation) {{
  navigator.geolocation.watchPosition(function(pos) {{
    var lat = pos.coords.latitude;
    var lon = pos.coords.longitude;
    if (!window.userMarker) {{
      window.userMarker = L.marker([lat, lon]).addTo(map);
      window.userCircle = L.circle([lat, lon], {{radius: pos.coords.accuracy, color: 'blue', fillOpacity: 0.1}}).addTo(map);
      map.setView([lat, lon], 17);
    }} else {{
      window.userMarker.setLatLng([lat, lon]);
      window.userCircle.setLatLng([lat, lon]);
      window.userCircle.setRadius(pos.coords.accuracy);
      map.setView([lat, lon], map.getZoom());  // Følg brugeren
    }}
  }},
  function(err){{
    console.log(err);
  }},
  {{
    enableHighAccuracy: true,
    maximumAge: 0,
    timeout: 5000
  }});
}} else {{
  alert("Din browser understøtter ikke GPS tracking");
}}
</script>
</body>
</html>
""", height=800)
