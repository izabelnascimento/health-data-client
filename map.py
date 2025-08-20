import os
import requests
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

# --- Configurações ---
YEAR = [2021, 2022, 2023, 2024]
BASE_URL_EFF = "http://localhost:8080/api/dea/indicators/first-semester/ranked?year={year}&rank=200"
BASE_URL_CITY = "http://localhost:8080/api/city"
GEOJSON_FILE = "resources/data/pe.json"  # seu arquivo corrigido
OUTPUT_FILE = "resources/map/"

os.makedirs("resources/map", exist_ok=True)

for year in YEAR:
    # --- Buscar lista de cidades ---
    print("🔎 Buscando lista de cidades...")
    resp_cities = requests.get(BASE_URL_CITY.format(year=year))
    resp_cities.raise_for_status()
    city_map = {str(c["id"]): c["name"].upper() for c in resp_cities.json()}

    # --- Buscar dados de eficiência ---
    print(f"🔎 Consultando dados de eficiência do ano {YEAR}...")
    resp_eff = requests.get(BASE_URL_EFF.format(year=year))
    resp_eff.raise_for_status()
    eff_data = resp_eff.json()
    df_eff = pd.DataFrame(eff_data)

    # Mapear cityId para nome de cidade
    df_eff["cityId"] = df_eff["cityId"].astype(str)
    df_eff["cityName"] = df_eff["cityId"].map(city_map)
    df_eff["cityName"] = df_eff["cityName"].str.upper()

    # --- Carregar GeoJSON ---
    geo_df = gpd.read_file(GEOJSON_FILE)
    geo_df["name"] = geo_df["name"].str.upper()  # garantir padronização

    # --- Merge: dados geográficos + eficiência
    merged = geo_df.merge(df_eff, left_on="name", right_on="cityName")

    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    merged.plot(
        column="efficiency",
        cmap="RdYlGn",
        linewidth=0.8,
        ax=ax,
        edgecolor="0.8",
        legend=True,
        legend_kwds={"label": "Eficiência DEA", "shrink": 0.6},
        vmin=0,  # força o início da escala no valor mínimo
        vmax=1   # força o fim da escala no valor máximo
    )

    ax.set_title(f"Mapa Temático de Eficiência por Município - {YEAR}", fontsize=14)
    ax.axis("off")

    plt.tight_layout()
    filename = os.path.join(OUTPUT_FILE, f"map_{year}.png")
    plt.savefig(filename, dpi=300)
    print(f"✅ Mapa salvo em {OUTPUT_FILE}")
