import requests
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

BASE_URL = "http://localhost:8080/api/dea/indicators/first-semester/ranked?year={year}&rank={rank}"
YEARS = [2021, 2022, 2023, 2024, 2025]
OUTPUT_DIR = "resources/v2/ranked"
RANK = 10

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Layout fixo 3 linhas x 2 colunas
fig, axes = plt.subplots(3, 2, figsize=(16, 14))
axes = axes.flatten()

for i, year in enumerate(YEARS):
    print(f"Querying year {year}...")

    response = requests.get(BASE_URL.format(year=year, rank=RANK))
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data)

    if "efficiency" not in df.columns:
        raise ValueError(f"JSON for year {year} must contain 'efficiency'.")

    ax = axes[i]

    # 🔹 Ordenar cidades por eficiência média
    df_ranked = (
        df.groupby("cityName", as_index=False)
          .agg({"efficiency": "mean"})
          .sort_values("efficiency", ascending=False)
    )

    cities_ordered = df_ranked["cityName"].tolist()

    # 🔹 Gerar cores viridis respeitando a ordem por eficiência
    cmap = plt.cm.viridis
    colors = cmap(np.linspace(0, 1, len(cities_ordered)))

    # 🔹 Plot respeitando a ordem correta
    for city, color in zip(cities_ordered, colors):
        city_data = df[df["cityName"] == city]

        ax.plot(
            city_data["bimonthly"],
            city_data["efficiency"],
            marker="o",
            linewidth=1.5,
            color=color,
            label=city
        )

    ax.set_xlabel("Bimester")
    ax.set_ylabel("Efficiency")
    ax.set_ylim(0, 1)
    ax.set_xticks([1, 2, 3])
    ax.set_title(f"Efficiency by City - 1st Semester {year}")
    ax.grid(True)

    # 🔹 Separar Top e Bottom corretamente
    handles, labels = ax.get_legend_handles_labels()

    top_handles = handles[:RANK]
    top_labels = labels[:RANK]

    bottom_handles = handles[-RANK:]
    bottom_labels = labels[-RANK:]

    legend1 = ax.legend(
        top_handles,
        top_labels,
        title=f"Top {RANK}",
        loc="upper left",
        bbox_to_anchor=(1.02, 1),
        fontsize=7,
        title_fontsize=9,
        frameon=True
    )
    ax.add_artist(legend1)

    ax.legend(
        bottom_handles,
        bottom_labels,
        title=f"Bottom {RANK}",
        loc="lower left",
        bbox_to_anchor=(1.02, 0),
        fontsize=7,
        title_fontsize=9,
        frameon=True
    )

# 🔹 Remover subplot vazio se existir
if len(YEARS) < len(axes):
    fig.delaxes(axes[-1])

plt.tight_layout(rect=[0, 0, 0.85, 1])
filename = os.path.join(OUTPUT_DIR, "efficiency_all_years.png")
plt.savefig(filename, dpi=300, bbox_inches="tight")
plt.close()

print(f"Combined chart saved at {filename}")