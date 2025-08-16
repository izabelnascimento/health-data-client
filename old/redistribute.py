import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

def redistribute_efficiency(original_df, top_cities, bottom_cities, max_efficiency=1.0):
    adjusted_df = original_df.copy()

    for month in range(1, 13):
        month_mask = adjusted_df['month'] == month
        top_mask = adjusted_df['city'].isin(top_cities) & month_mask
        bottom_mask = adjusted_df['city'].isin(bottom_cities) & month_mask

        top_month = adjusted_df[top_mask].copy()
        bottom_month = adjusted_df[bottom_mask]

        top_month['surplus'] = (top_month['efficiency'] - max_efficiency).clip(lower=0)
        total_surplus = top_month['surplus'].sum()

        for idx, row in top_month.iterrows():
            adjusted_df.at[idx, 'efficiency'] = min(row['efficiency'], max_efficiency)

        if not bottom_month.empty and total_surplus > 0:
            gain_per_city = total_surplus / len(bottom_month)
            for idx, row in bottom_month.iterrows():
                adjusted_df.at[idx, 'efficiency'] = row['efficiency'] + gain_per_city

    return adjusted_df

output_dir = "comparative"
os.makedirs(output_dir, exist_ok=True)

for year in range(2021, 2025):
    url = f"http://localhost:8080/api/efficiency/ranked/{year}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch data for {year}: {response.status_code}")
        continue

    ranked_data = response.json()
    records = []

    for group in ['top', 'down']:
        for city_data in ranked_data.get(group, []):
            city_name = city_data['city']['name']
            for efficiency in city_data['efficiencies']:
                records.append({
                    'city': city_name,
                    'month': efficiency['month'],
                    'efficiency': efficiency['efficiency'],
                    'group': group
                })

    df_actual = pd.DataFrame(records)
    top_cities = df_actual[df_actual['group'] == 'top']['city'].unique()
    bottom_cities = df_actual[df_actual['group'] == 'down']['city'].unique()
    df_predicted = redistribute_efficiency(df_actual, top_cities, bottom_cities)

    plt.figure(figsize=(12, 6))
    colors = plt.cm.tab10.colors
    color_map = {city: colors[i % len(colors)] for i, city in enumerate(df_actual['city'].unique())}

    top_handles, bottom_handles = [], []

    for city in df_actual['city'].unique():
        actual = df_actual[df_actual['city'] == city].sort_values('month')
        predicted = df_predicted[df_predicted['city'] == city].sort_values('month')
        color = color_map[city]

        line_actual, = plt.plot(actual['month'], actual['efficiency'], label=f"{city} (actual)", color=color)
        line_predicted, = plt.plot(predicted['month'], predicted['efficiency'], linestyle='dotted', label=f"{city} (predicted)", color=color)

        if city in top_cities:
            top_handles.append((line_actual, line_predicted))
        else:
            bottom_handles.append((line_actual, line_predicted))

    # Create custom legends
    top_lines = [Line2D([0], [0], color=color_map[city], label=city) for city in top_cities]
    top_dots = [Line2D([0], [0], color=color_map[city], linestyle='dotted', label=f"{city} (predicted)") for city in top_cities]

    bottom_lines = [Line2D([0], [0], color=color_map[city], label=city) for city in bottom_cities]
    bottom_dots = [Line2D([0], [0], color=color_map[city], linestyle='dotted', label=f"{city} (predicted)") for city in bottom_cities]

    first_legend = plt.legend(handles=top_lines + top_dots, title='Top Cities', loc='upper left', bbox_to_anchor=(1.02, 1))
    second_legend = plt.legend(handles=bottom_lines + bottom_dots, title='Bottom Cities', loc='lower left', bbox_to_anchor=(1.02, 0))

    plt.gca().add_artist(first_legend)  # Add the first legend manually

    plt.title(f"Actual vs Predicted Efficiency - {year}")
    plt.xlabel("Month")
    plt.ylabel("Efficiency")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/efficiency_comparison_{year}.png", bbox_inches='tight')
    plt.close()
