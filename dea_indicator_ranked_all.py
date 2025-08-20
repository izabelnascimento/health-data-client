import requests
import pandas as pd
import matplotlib.pyplot as plt
import os

BASE_URL = "http://localhost:8080/api/dea/indicators/first-semester/ranked?year={year}&rank={rank}"
YEARS = [2021, 2022, 2023, 2024]
OUTPUT_DIR = "resources/ranked"
RANK = 10

os.makedirs(OUTPUT_DIR, exist_ok=True)

fig, axes = plt.subplots(2, 2, figsize=(18, 12))
axes = axes.flatten()

for i, year in enumerate(YEARS):
    print(f"Consultando ano {year}...")
    response = requests.get(BASE_URL.format(year=year, rank=RANK))
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data)

    if "efficiency" not in df.columns:
        raise ValueError(f"O JSON do ano {year} precisa conter o campo 'efficiency'.")

    ax = axes[i]

    for city, city_data in df.groupby("cityName"):
        ax.plot(
            city_data["bimonthly"],
            city_data["efficiency"],
            marker="o",
            linewidth=1,
            label=city
        )

    ax.set_xlabel("Bimestre")
    ax.set_ylabel("Eficiência")
    ax.set_title(f"Eficiência por Cidade - 1º Semestre {year}")
    ax.grid(True)
    ax.set_xticks([1, 2, 3])

    handles, labels = ax.get_legend_handles_labels()
    top_handles, top_labels = handles[:RANK], labels[:RANK]
    bottom_handles, bottom_labels = handles[RANK:], labels[RANK:]

    legend1 = ax.legend(
        top_handles, top_labels,
        title=f"Top {RANK} ({year})",
        loc="upper left",
        bbox_to_anchor=(1.02, 1),
        fontsize=8,
        title_fontsize=10,
        frameon=True
    )
    ax.add_artist(legend1)

    ax.legend(
        bottom_handles, bottom_labels,
        title=f"Bottom {RANK} ({year})",
        loc="lower left",
        bbox_to_anchor=(1.02, 0),
        fontsize=8,
        title_fontsize=10,
        frameon=True
    )

plt.tight_layout(rect=[0, 0, 0.85, 1])
filename = os.path.join(OUTPUT_DIR, "efficiency_all_years.png")
plt.savefig(filename, dpi=300, bbox_inches="tight")
plt.close()
print(f"✅ Gráfico combinado salvo em {filename}")
