import os

import requests
import pandas as pd
import matplotlib.pyplot as plt

BASE_URL = "http://localhost:8080/api/dea/indicators/first-semester/ranked?year={year}&rank={rank}"
YEARS = [2021, 2022, 2023, 2024]
OUTPUT_DIR = "resources/scatter"
RANK = 30

os.makedirs(OUTPUT_DIR, exist_ok=True)

for year in YEARS:
    print(f"Consultando ano {year}...")
    response = requests.get(BASE_URL.format(year=year, rank=RANK))
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data)

    df = df.groupby("cityName", as_index=False).agg({
        "apsPerCapita": "mean",
        "productivity": "mean",
        "efficiency": "mean"
    })

    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(
        df["apsPerCapita"],
        df["productivity"],
        c=df["efficiency"],
        cmap="RdYlGn",
        s=300,
        alpha=0.8,
        edgecolor="k"
    )

    for i, row in df.iterrows():
        plt.text(row["apsPerCapita"], row["productivity"], row["cityName"],
                 fontsize=9, ha="right")

    plt.colorbar(scatter, label="Eficiência")
    plt.xlabel("Orçamento da APS per capita (input)")
    plt.ylabel("Produtividade (output)")
    plt.title(f"Dispersão: APS per capita vs Produtividade - 1º Semestre {year}")
    plt.grid(True)
    plt.tight_layout()
    filename = os.path.join(OUTPUT_DIR, f"dispersion_{year}.png")
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"Gráfico salvo em {filename}")
