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

for year in YEARS:
    print(f"🔎 Consultando ano {year}...")

    response = requests.get(BASE_URL.format(year=year, rank=RANK))
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data)

    # Corrigir o nome da coluna de cobertura
    cols = [
        "apsPerCapita",
        "teamsDensity",
        "healthCareVisitsPerThousandReais",
        "cobertura",  # <-- aqui está corrigido
        "productivity",
        "efficiency"
    ]

    # Verifica se todas as colunas estão presentes
    missing_cols = [col for col in cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Colunas ausentes no DataFrame: {missing_cols}")

    df_corr = df[cols]

    # Mapa de correlação
    plt.figure(figsize=(10, 7))
    sns.heatmap(
        df_corr.corr(),
        annot=True,
        cmap="RdYlGn",
        vmin=-1, vmax=1,
        fmt=".2f", linewidths=0.5
    )
    plt.title(f"Correlação entre Inputs, Outputs e Eficiência - 1º Semestre {year}")
    plt.tight_layout()

    filename = os.path.join(OUTPUT_DIR, f"correlation_{year}.png")
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"✅ Mapa de correlação salvo em {filename}")
