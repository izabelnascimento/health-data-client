import requests
import pandas as pd
import matplotlib.pyplot as plt
import os

BASE_URL = "http://localhost:8080/api/dea/indicators/first-semester/ranked?year={year}"
YEARS = [2021, 2022, 2023, 2024]
OUTPUT_DIR = "resources/ranked"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for year in YEARS:
    print(f"Consultando ano {year}...")
    response = requests.get(BASE_URL.format(year=year))
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data)

    if "efficiency" not in df.columns:
        raise ValueError(f"O JSON do ano {year} precisa conter o campo 'efficiency'.")

    plt.figure(figsize=(14, 8))

    for city, city_data in df.groupby("cityName"):
        plt.plot(
            city_data["bimonthly"],
            city_data["efficiency"],
            marker="o",
            linewidth=1,
            label=city
        )

    plt.xlabel("Bimestre")
    plt.ylabel("Eficiência")
    plt.title(f"Eficiência por Cidade ao longo dos Bimestres - 1º Semestre {year}")
    plt.grid(True)

    handles, labels = plt.gca().get_legend_handles_labels()

    top_handles, top_labels = handles[:5], labels[:5]
    bottom_handles, bottom_labels = handles[5:], labels[5:]

    legend1 = plt.legend(
        top_handles, top_labels,
        title="Top 5",
        loc="upper left",
        bbox_to_anchor=(1.02, 1),
        fontsize=10,
        title_fontsize=12
    )
    plt.gca().add_artist(legend1)

    plt.legend(
        bottom_handles, bottom_labels,
        title="Bottom 5",
        loc="lower left",
        bbox_to_anchor=(1.02, 0),
        fontsize=10,
        title_fontsize=12
    )

    plt.tight_layout()  # espaço para as duas caixas
    filename = os.path.join(OUTPUT_DIR, f"efficiency_{year}.png")
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"Gráfico salvo em {filename}")
