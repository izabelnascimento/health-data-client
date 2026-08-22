import os
import requests
import pandas as pd
import matplotlib.pyplot as plt

BASE_URL = "http://localhost:8080/api/dea/indicators/first-semester/ranked?year={year}&rank={rank}"
YEARS = [2021, 2022, 2023, 2024, 2025]
# Caminho ancorado na localização do próprio script (não na pasta de onde ele
# é executado), para sempre salvar na pasta resources/ que já existe na raiz
# do projeto, mesmo se o script for rodado de dentro de src/.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "resources", "v2", "scatter")
RANK = 30

os.makedirs(OUTPUT_DIR, exist_ok=True)

cmap = "viridis"

for year in YEARS:
    print(f"Querying year {year}...")
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
        cmap=cmap,
        s=300,
        alpha=0.8,
        edgecolor="k"
    )

    for i, row in df.iterrows():
        plt.text(
            row["apsPerCapita"],
            row["productivity"],
            row["cityName"],
            fontsize=20,
            ha="right"
        )

    cbar = plt.colorbar(scatter, label="Efficiency")
    cbar.set_label("Efficiency", fontsize=15)
    cbar.ax.tick_params(labelsize=15)
    plt.xlabel("PHC Budget per Capita (Input)", fontsize=20)
    plt.ylabel("Productivity (Output)", fontsize=20)
    plt.title(f"Scatter Plot: PHC Budget per Capita vs Productivity - 1st Semester {year}", fontsize=15)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.grid(True)
    plt.tight_layout()

    filename = os.path.join(OUTPUT_DIR, f"scatter_{year}.png")
    plt.savefig(filename, dpi=300)
    plt.close()

    print(f"Chart saved at {filename}")