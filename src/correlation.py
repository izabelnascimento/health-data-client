import os
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

BASE_URL = "http://localhost:8080/api/dea/indicators/first-semester/ranked?year={year}&rank={rank}"
YEARS = [2021, 2022, 2023, 2024, 2025]
OUTPUT_DIR = "../resources/v2/correlation"
RANK = 30

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Column renaming for English labels
rename_cols = {
    "apsPerCapita": "PHC Budget per Capita",
    "teamsDensity": "Team Density",
    "healthCareVisitsPerThousandReais": "Health Visits per 1k BRL",
    "cobertura": "Coverage (%)",
    "productivity": "Productivity",
    "efficiency": "Efficiency"
}

for year in YEARS:
    print(f"🔎 Querying year {year}...")

    response = requests.get(BASE_URL.format(year=year, rank=RANK))
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data)

    cols = list(rename_cols.keys())

    # Check if all required columns exist
    missing_cols = [col for col in cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns in DataFrame: {missing_cols}")

    # Rename columns for visualization
    df_corr = df[cols].rename(columns=rename_cols)

    # Correlation heatmap
    plt.figure(figsize=(10, 7))
    sns.heatmap(
        df_corr.corr(),
        annot=True,
        cmap="viridis",   # Updated colormap
        vmin=-1,
        vmax=1,
        fmt=".2f",
        linewidths=0.5
    )

    plt.title(f"Correlation between Inputs, Outputs and Efficiency - 1st Semester {year}")
    plt.tight_layout()

    filename = os.path.join(OUTPUT_DIR, f"correlation_{year}.png")
    plt.savefig(filename, dpi=300)
    plt.close()

    print(f"Correlation heatmap saved at {filename}")