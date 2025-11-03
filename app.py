import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Parkeringskort Esbjerg",
    page_icon="🚗",
    layout="wide"
)

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
  #followButton {{
    position: absolute;
    bottom: 20px;
    left: 20px;
    z-index: 1000;
    background-color: white;
    border: 1px solid #ccc;
    border-radius: 8px;
    padding: 8px 12px;
    cursor: pointer;
    font-weight: bold;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
  }}
  #followButton.active {{
    background-color: #007bff;
    color: white;
    border-color: #007bff;
  }}
</style>
</head>
<body>
<div id="map"></div>
<button id="followButton">🔒 Følg mig: Fra</button>

<script>
// Opret kort uden center til at starte med
var map = L.map('map');

// OpenStreetMap lag
L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
  maxZoom: 19,
}}).addTo(map);

// Data fra Python
var points = {json_data};

// Tilføj røde/grønne prikker
points.forEach(p => {{
  var color = p.betalt == 1 ? 'green' : 'red';
  L.circleMarker([p.lat, p.lon], {{
    radius: 9,
    color: color,
    fillOpacity: 0
  }}).addTo(map);
}});

let followMode = false;
const followButton = document.getElementById("followButton");

followButton.addEventListener("click", () => {{
  followMode = !followMode;
  if (followMode) {{
    followButton.classList.add("active");
    followButton.innerText = "🟢 Følg mig: Til";
  }} else {{
    followButton.classList.remove("active");
    followButton.innerText = "🔒 Følg mig: Fra";
  }}
}});

// GPS tracking og initial centrering
if (navigator.geolocation) {{
  navigator.geolocation.getCurrentPosition(function(pos) {{
    var lat = pos.coords.latitude;
    var lon = pos.coords.longitude;
    map.setView([lat, lon], 17); // start dér hvor brugeren er
  }});

  navigator.geolocation.watchPosition(function(pos) {{
    var lat = pos.coords.latitude;
    var lon = pos.coords.longitude;

    if (!window.userMarker) {{
      window.userMarker = L.marker([lat, lon]).addTo(map);
      window.userCircle = L.circle([lat, lon], {{
        radius: pos.coords.accuracy,
        color: 'blue',
        fillOpacity: 0.1
      }}).addTo(map);
    }} else {{
      window.userMarker.setLatLng([lat, lon]);
      window.userCircle.setLatLng([lat, lon]);
      window.userCircle.setRadius(pos.coords.accuracy);
    }}

    if (followMode) {{
      map.setView([lat, lon], map.getZoom());
    }}
  }},
  function(err){{
    console.warn("GPS-fejl:", err);
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
