import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import requests
import os
from statistics import mode, StatisticsError

YEARS = [2021, 2022, 2023, 2024]
BASE_URL_EFF = "http://localhost:8080/api/dea/indicators/first-semester/ranked?year={year}&rank=200"
BASE_URL_CITY = "http://localhost:8080/api/city"
GEOJSON_FILE = "resources/data/pe.json"
OUTPUT_FILE = "resources/map/map_stats_text.png"

os.makedirs("resources/map", exist_ok=True)

resp_cities = requests.get(BASE_URL_CITY)
resp_cities.raise_for_status()
city_map = {str(c["id"]): c["name"].upper() for c in resp_cities.json()}

fig, axes = plt.subplots(len(YEARS), 1, figsize=(12, 20))

cmap = "RdYlGn"
vmin, vmax = 0, 1

if len(YEARS) == 1:
    axes = [axes]

for i, year in enumerate(YEARS):
    print(f"Consultando ano {year}...")

    resp_eff = requests.get(BASE_URL_EFF.format(year=year))
    resp_eff.raise_for_status()
    eff_data = resp_eff.json()
    df_eff = pd.DataFrame(eff_data)

    df_eff["cityId"] = df_eff["cityId"].astype(str)
    df_eff["cityName"] = df_eff["cityId"].map(city_map)
    df_eff["cityName"] = df_eff["cityName"].str.upper()

    geo_df = gpd.read_file(GEOJSON_FILE)
    geo_df["name"] = geo_df["name"].str.upper()
    merged = geo_df.merge(df_eff, left_on="name", right_on="cityName")

    merged.plot(
        column="efficiency",
        cmap=cmap,
        linewidth=0.5,
        ax=axes[i],
        edgecolor="0.8",
        legend=False,
        legend_kwds={"label": "Eficiência DEA", "orientation": "horizontal", "shrink": 0.6},
        vmin=0,
        vmax=1
    )
    axes[i].set_title(f"Eficiência por Município - {year}", fontsize=14)
    axes[i].axis("off")

    mean_val = df_eff["efficiency"].mean()
    try:
        mode_val = mode(round(v, 2) for v in df_eff["efficiency"])
    except StatisticsError:
        mode_val = None

    stats_text = (
        f"Média: {mean_val:.2f}\n"
        f"Moda: {mode_val:.2f}" if isinstance(mode_val, float) else "Moda: N/A"
    )

    axes[i].text(
        0.02, 0.05, stats_text,
        transform=axes[i].transAxes,
        fontsize=13,
        fontweight="bold",
        va="bottom",
        ha="left",
        linespacing=1.5,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="black", alpha=0.8)
    )

cbar_ax = fig.add_axes([0.25, 0.92, 0.5, 0.01])
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
cbar = fig.colorbar(sm, cax=cbar_ax, orientation="horizontal")
cbar.set_label("Eficiência DEA", fontsize=11)

plt.tight_layout(rect=[0, 0, 1, 0.9])
plt.savefig(OUTPUT_FILE, dpi=300)
plt.close()
print(f"Arquivo salvo em {OUTPUT_FILE}")
