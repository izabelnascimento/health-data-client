import os
import requests
import pandas as pd
import matplotlib.pyplot as plt

def redistribuir_eficiencia(original_df, top_cities, down_cities, max_efficiency=1.0):
    df_novo = original_df.copy()

    for month in range(1, 13):
        month_mask = df_novo['month'] == month
        top_mask = df_novo['city'].isin(top_cities) & month_mask
        down_mask = df_novo['city'].isin(down_cities) & month_mask

        top_month = df_novo[top_mask]
        down_month = df_novo[down_mask]

        top_month = top_month.copy()
        top_month['excedente'] = (top_month['efficiency'] - max_efficiency).clip(lower=0)
        total_excedente = top_month['excedente'].sum()

        for idx, row in top_month.iterrows():
            nova = min(row['efficiency'], max_efficiency)
            df_novo.at[idx, 'efficiency'] = nova

        if not down_month.empty and total_excedente > 0:
            ganho_por_cidade = total_excedente / len(down_month)
            for idx, row in down_month.iterrows():
                nova = row['efficiency'] + ganho_por_cidade
                df_novo.at[idx, 'efficiency'] = nova

    return df_novo

for year in range(2021, 2025):
    url = f"http://localhost:8080/api/efficiency/ranked/{year}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Erro ao buscar dados de {year}: {response.status_code}")
        continue

    ranked_data = response.json()
    rows = []

    for group in ['top', 'down']:
        for city_data in ranked_data.get(group, []):
            city_name = city_data['city']['name']
            for efficiency in city_data['efficiencies']:
                rows.append({
                    'city': city_name,
                    'month': efficiency['month'],
                    'efficiency': efficiency['efficiency'],
                    'group': group
                })

    df = pd.DataFrame(rows)
    top_cities = df[df['group'] == 'top']['city'].unique()
    down_cities = df[df['group'] == 'down']['city'].unique()

    # Gráfico Original
    plt.figure(figsize=(12, 6))
    for city, group_df in df.groupby('city'):
        plt.plot(group_df['month'], group_df['efficiency'], label=city, marker='o')
    plt.title(f"Eficiência Original - {year}")
    plt.xlabel("Mês")
    plt.ylabel("Eficiência")
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small')
    plt.tight_layout()
    plt.grid(True)
    os.makedirs("predictions", exist_ok=True)
    plt.savefig(f"resources/predictions/original_efficiency_{year}.png")
    plt.close()

    df_ajustado = redistribuir_eficiencia(df, top_cities, down_cities, max_efficiency=1.0)

    plt.figure(figsize=(12, 6))
    for city, group_df in df_ajustado.groupby('city'):
        plt.plot(group_df['month'], group_df['efficiency'], label=city, marker='o')
    plt.title(f"Eficiência Pós-Realoação - {year}")
    plt.xlabel("Mês")
    plt.ylabel("Eficiência")
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small')
    plt.tight_layout()
    plt.grid(True)
    plt.savefig(f"resources/predictions/adjusted_efficiency_{year}.png")
    plt.close()
