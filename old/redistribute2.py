import os
import requests
import matplotlib.pyplot as plt

# ==== Config ====
BASE_URL = "http://localhost:8080/api/efficiency/ranked/redistribute"
YEARS = [2021, 2022, 2023, 2024]
OUTPUT_DIR = "redistribution2"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_redistributed(year: int) -> dict:
    """GET {BASE_URL}/{year} -> estrutura com 'real' e 'redistributed'."""
    url = f"{BASE_URL}/{year}"
    resp = requests.post(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _series_from_city_block(city_block: dict):
    """Extrai (months, efficiencies) já ordenados por mês de um bloco de cidade."""
    effs = sorted(city_block.get("efficiencies", []), key=lambda e: e["month"])
    months = [e["month"] for e in effs]
    values = [e["efficiency"] for e in effs]
    return months, values


def _find_city_block(by_group_list: list, city_name: str) -> dict | None:
    """Encontra o bloco da cidade pelo nome dentro de uma lista de cidades."""
    for c in by_group_list:
        if c["city"]["name"] == city_name:
            return c
    return None


def plot_year(data: dict, year: int):
    """
    Plota um gráfico para o ano:
      - Real: linha contínua
      - Redistributed: linha pontilhada
      - Mesma cor para a dupla (real/redistributed) de cada cidade
      - Duas legendas (Top/Melhores e Down/Piores)
    """
    real_top = data["real"]["top"]
    real_down = data["real"]["down"]
    red_top = data["redistributed"]["top"]
    red_down = data["redistributed"]["down"]

    fig, ax = plt.subplots(figsize=(12, 6))

    # Ajuste de margem direita para acomodar as duas legendas
    plt.subplots_adjust(right=0.72)

    # Cores separadas para top e down (usando cycles independentes)
    top_colors = iter(plt.rcParams['axes.prop_cycle'].by_key()['color'])
    down_colors = iter(plt.rcParams['axes.prop_cycle'].by_key()['color'])

    handles_top, labels_top = [], []
    handles_down, labels_down = [], []

    # --- TOP (Melhores) ---
    for city_block in real_top:
        city_name = city_block["city"]["name"]
        color = next(top_colors)

        # Real
        m_real, v_real = _series_from_city_block(city_block)
        line_real, = ax.plot(m_real, v_real, linestyle='-', color=color)
        handles_top.append(line_real)
        labels_top.append(f"{city_name} — real")

        # Redistributed (mesma cor, pontilhado)
        red_block = _find_city_block(red_top, city_name)
        if red_block:
            m_red, v_red = _series_from_city_block(red_block)
            line_red, = ax.plot(m_red, v_red, linestyle=':', color=color)
            handles_top.append(line_red)
            labels_top.append(f"{city_name} — redistributed")

    # --- DOWN (Piores) ---
    for city_block in real_down:
        city_name = city_block["city"]["name"]
        color = next(down_colors)

        # Real
        m_real, v_real = _series_from_city_block(city_block)
        line_real, = ax.plot(m_real, v_real, linestyle='-', color=color)
        handles_down.append(line_real)
        labels_down.append(f"{city_name} — real")

        # Redistributed (mesma cor, pontilhado)
        red_block = _find_city_block(red_down, city_name)
        if red_block:
            m_red, v_red = _series_from_city_block(red_block)
            line_red, = ax.plot(m_red, v_red, linestyle=':', color=color)
            handles_down.append(line_red)
            labels_down.append(f"{city_name} — redistributed")

    # Eixos e título
    ax.set_title(f"Real vs Redistributed Efficiency — {year}")
    ax.set_xlabel("Month")
    ax.set_ylabel("Efficiency")
    ax.grid(True)
    ax.set_xticks(range(1, 13))

    # Duas legendas (Top e Down) posicionadas na direita
    leg_top = ax.legend(handles_top, labels_top, title="Top (best)", loc='upper left',
                        bbox_to_anchor=(1.02, 1.0), fontsize='small', title_fontsize='small', frameon=True)
    ax.add_artist(leg_top)
    leg_down = ax.legend(handles_down, labels_down, title="Bottom (worst)", loc='upper left',
                         bbox_to_anchor=(1.02, 0.5), fontsize='small', title_fontsize='small', frameon=True)

    # Salvar arquivos
    png_path = os.path.join(OUTPUT_DIR, f"real_vs_redistributed_{year}.png")
    plt.savefig(png_path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Saved: {png_path}")


def main():
    for year in YEARS:
        try:
            data = fetch_redistributed(year)
            plot_year(data, year)
        except Exception as e:
            print(f"[{year}] Error: {e}")


if __name__ == "__main__":
    main()
