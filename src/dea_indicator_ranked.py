import requests
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

BASE_URL = "http://localhost:8080/api/dea/indicators/first-semester/ranked?year={year}&rank={rank}"
YEARS = [2021, 2022, 2023, 2024, 2025]
OUTPUT_DIR = "../resources/v2/ranked"
RANK = 10

os.makedirs(OUTPUT_DIR, exist_ok=True)

for year in YEARS:
    print(f"Querying year {year}...")
    response = requests.get(BASE_URL.format(year=year, rank=RANK))
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data)

    if "efficiency" not in df.columns:
        raise ValueError(f"JSON for year {year} must contain 'efficiency'.")

    plt.figure(figsize=(10, 8))

    # 🔹 Ordenar cidades por eficiência média (decrescente)
    df_ranked = (
        df.groupby("cityName", as_index=False)
          .agg({"efficiency": "mean"})
          .sort_values("efficiency", ascending=False)
    )

    cities_ordered = df_ranked["cityName"].tolist()

    # 🔹 Gerar cores viridis respeitando a ordem
    colors = plt.cm.viridis(np.linspace(0, 1, len(cities_ordered)))

    # 🔹 Plot respeitando ordem por eficiência
    for city, color in zip(cities_ordered, colors):
        city_data = df[df["cityName"] == city]
        plt.plot(
            city_data["bimonthly"],
            city_data["efficiency"],
            marker="o",
            linewidth=1.5,
            label=city,
            color=color
        )

    plt.xlabel("Bimester")
    plt.ylabel("Efficiency")
    plt.title(f"Efficiency by City Across Bimesters - 1st Semester {year}")
    plt.grid(True)
    plt.ylim(0, 1)
    plt.xticks([1, 2, 3])

    handles, labels = plt.gca().get_legend_handles_labels()

    # 🔹 Top = maiores
    top_handles = handles[:RANK]
    top_labels = labels[:RANK]

    # 🔹 Bottom = menores
    bottom_handles = handles[-RANK:]
    bottom_labels = labels[-RANK:]

    legend1 = plt.legend(
        top_handles,
        top_labels,
        title=f"Top {RANK}",
        loc="upper left",
        bbox_to_anchor=(1.02, 1),
        fontsize=10,
        title_fontsize=12,
        frameon=True
    )
    plt.gca().add_artist(legend1)

    plt.legend(
        bottom_handles,
        bottom_labels,
        title=f"Bottom {RANK}",
        loc="lower left",
        bbox_to_anchor=(1.02, 0),
        fontsize=10,
        title_fontsize=12,
        frameon=True
    )

    plt.tight_layout()
    plt.subplots_adjust(right=0.75)

    filename = os.path.join(OUTPUT_DIR, f"efficiency_{year}.png")
    plt.savefig(filename, dpi=300)
    plt.close()

    print(f"Chart saved at {filename}")