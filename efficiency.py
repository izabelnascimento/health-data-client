import os

import requests
import pandas as pd
import matplotlib.pyplot as plt

for year in range(2021, 2025):
    url = f"http://localhost:8080/api/efficiency/{year}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Erro ao buscar dados de {year}: {response.status_code}")
        continue

    data = response.json()

    rows = []
    for city in data:
        city_name = city['city']['name']
        for efficiency in city['efficiencies']:
            rows.append({
                'city': city_name,
                'month': efficiency['month'],
                'efficiency': efficiency['efficiency']
            })

    df = pd.DataFrame(rows)

    plt.clf()

    for city, group in df.groupby('city'):
        plt.plot(group['month'], group['efficiency'], label=city)

    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small', ncol=4)
    plt.xlabel('Mês')
    plt.ylabel('Eficiência')
    plt.title(f"Eficiência por Cidade ({year})")

    output_dir = "resources/efficiency"
    os.makedirs(output_dir, exist_ok=True)
    plt.grid(True)
    plt.savefig(f"{output_dir}/efficiency_{year}.pdf", bbox_inches='tight')
    plt.show()
