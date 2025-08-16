import os

import requests
import pandas as pd
import matplotlib.pyplot as plt

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

    plt.figure(figsize=(10, 6))
    for city, group_df in df.groupby('city'):
        plt.plot(group_df['month'], group_df['efficiency'], label=city)

    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small')
    plt.xlabel('Mês')
    plt.ylabel('Eficiência')
    plt.title(f"Top 5 e Bottom 5 Cidades ({year})")
    plt.grid(True)
    plt.tight_layout()

    output_dir = "ranked"
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(f"{output_dir}/ranked_efficiency_{year}.pdf", bbox_inches='tight')
    plt.show()
