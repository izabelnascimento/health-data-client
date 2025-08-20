import os
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

BASE_URL = "http://localhost:8080/api/dea/indicators/first-semester/ranked?year={year}&rank={rank}"
YEARS = [2021, 2022, 2023, 2024]
OUTPUT_DIR = "resources/correlation"
RANK = 30

os.makedirs(OUTPUT_DIR, exist_ok=True)

rename_cols = {
    "apsPerCapita": "Orçamento APS per capita",
    "teamsDensity": "Densidade de equipes",
    "healthCareVisitsPerThousandReais": "Qtd consultas por mil R$",
    "cobertura": "Cobertura (%)",
    "productivity": "Produtividade",
    "efficiency": "Eficiência"
}

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

cmap = "RdYlGn"
vmin, vmax = -1, 1

for i, year in enumerate(YEARS):
    print(f"🔎 Consultando ano {year}...")

    response = requests.get(BASE_URL.format(year=year, rank=RANK))
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data)

    cols = list(rename_cols.keys())

    missing_cols = [col for col in cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Colunas ausentes no DataFrame: {missing_cols}")

    df_corr = df[cols].rename(columns=rename_cols)

    sns.heatmap(
        df_corr.corr(),
        annot=True,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        fmt=".2f", linewidths=0.5,
        ax=axes[i],
        cbar=False
    )
    axes[i].set_title(f"Correlação - {year}", fontsize=14)

cbar_ax = fig.add_axes([0.25, 0.94, 0.5, 0.02])
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
cbar = fig.colorbar(sm, cax=cbar_ax, orientation="horizontal")
cbar.set_label("Correlação (inputs, outputs e eficiência)", fontsize=12, labelpad=6)

plt.tight_layout(rect=[0, 0, 1, 0.88])

filename = os.path.join(OUTPUT_DIR, "correlation_all_years.png")
plt.savefig(filename, dpi=300)
plt.close()
print(f"Mapa de correlação combinado salvo em {filename}")
