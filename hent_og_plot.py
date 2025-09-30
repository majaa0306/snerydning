import requests
import pandas as pd
import folium

# --- Hent alle adresser ---
base_url = "https://api.dataforsyningen.dk/adresser"
params = {"postnr": "6823", "per_side": 500}
page = 1
rows = []

while True:
    params["side"] = page
    response = requests.get(base_url, params=params)
    data = response.json()
    if not data:
        break

    for d in data:
        adresse = d.get("adressebetegnelse")
        adgangsadresse = d.get("adgangsadresse", {})
        adgangspunkt = adgangsadresse.get("adgangspunkt", {})
        coords = adgangspunkt.get("koordinater")

        if coords:
            lon, lat = coords[0], coords[1]
            rows.append({"adresse": adresse, "lat": lat, "lon": lon, "betalt": 0})

    page += 1

df = pd.DataFrame(rows)
df.to_csv(
    "ansager_adresser.csv",
    index=False,
    encoding="utf-8",
    sep=";",       # bruger semikolon som kolonne-separator
    decimal=",",   # bruger komma som decimalseparator
    quoting=1      # sikrer at tekst med kommaer pakkes ind i ""
)
print(f"Gemte {len(df)} adresser i ansager_adresser.csv")
