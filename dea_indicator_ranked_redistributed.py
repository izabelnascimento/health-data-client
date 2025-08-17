import requests
import pandas as pd
import matplotlib.pyplot as plt
import os

# --- Configuração ---
BASE_URL_REAL = "http://localhost:8080/api/dea/indicators/first-semester/ranked?year={year}&rank={rank}"
BASE_URL_REDIS = "http://localhost:8080/api/dea/indicators/first-semester/ranked/redistributed?year={year}&rank={rank}"
YEARS = [2021, 2022, 2023, 2024]   # pode incluir [2021, 2022, 2023, 2024]
OUTPUT_DIR = "resources/ranked"
RANK = 3

os.makedirs(OUTPUT_DIR, exist_ok=True)

for year in YEARS:
    print(f"🔎 Consultando ano {year}...")

    # --- Consulta dados reais ---
    resp_real = requests.get(BASE_URL_REAL.format(year=year, rank=RANK))
    resp_real.raise_for_status()
    real_data = resp_real.json()
    df_real = pd.DataFrame(real_data)

    if df_real.empty or "efficiency" not in df_real.columns:
        raise ValueError(f"O JSON real do ano {year} está vazio ou sem 'efficiency'.")

    # --- Consulta dados redistribuídos ---
    resp_redis = requests.post(BASE_URL_REDIS.format(year=year, rank=RANK))
    resp_redis.raise_for_status()
    redis_data = resp_redis.json()
    df_redis = pd.DataFrame(redis_data)

    if df_redis.empty or "efficiency" not in df_redis.columns:
        raise ValueError(f"O JSON redistribuído do ano {year} está vazio ou sem 'efficiency'.")

    # --- Merge pelo cityId + bimonthly ---
    df_merge = df_real.merge(
        df_redis,
        on=["cityId", "bimonthly"],
        how="inner",
        suffixes=("_real", "_redis")
    )

    # Agora já temos cityName herdado do df_real
    # colunas: cityId, cityName, bimonthly, efficiency_real, efficiency_redis, ...

    # --- Plot ---
    plt.figure(figsize=(12, 7))

    # Para cada cidade, plota real (linha sólida) e redistribuído (linha pontilhada)
    for city, city_data in df_merge.groupby("cityName"):
        plt.plot(
            city_data["bimonthly"],
            city_data["efficiency_real"],
            marker="o",
            linewidth=1.8,
            label=f"{city} (Real)"
        )
        plt.plot(
            city_data["bimonthly"],
            city_data["efficiency_redis"],
            marker="x",
            linestyle="--",
            linewidth=1.5,
            label=f"{city} (Redistribuído)"
        )

    plt.xlabel("Bimestre")
    plt.ylabel("Eficiência")
    plt.title(f"Eficiência Real vs Redistribuída - 1º Semestre {year}")
    plt.xticks(sorted(df_merge["bimonthly"].unique()))
    plt.grid(True, linestyle="--", alpha=0.6)

    # Legenda à direita
    plt.legend(
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        fontsize=9,
        title="Cidades"
    )

    plt.tight_layout(rect=[0, 0, 0.8, 1])
    filename = os.path.join(OUTPUT_DIR, f"efficiency_comparison_{year}.png")
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"✅ Gráfico salvo em {filename}")
