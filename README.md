## health-data-client

The **health-data-client** application corresponds to the analytical layer of the HERO architecture. It consumes data from the ETL service and performs efficiency analysis using Data Envelopment Analysis (DEA), generating rankings, correlation analyses, spatial visualizations, and decision-support outputs.

This application depends on the ETL pipeline for data integration:

➡️ ETL service: https://github.com/izabelnascimento/health-data-etl

### ⚙️ Requirements

- Python 3.10+ (this project's virtual environment was built with 3.10)
- The Python packages listed in [`requirements.txt`](requirements.txt):

| Package | Version | Used for |
| --- | --- | --- |
| `requests` | 2.32.4 | Calling the health-data-etl REST API |
| `pandas` | 2.3.1 | Tabular data handling |
| `numpy` | 2.2.6 | Numeric arrays / color scaling |
| `matplotlib` | 3.10.3 | Charts and maps |
| `seaborn` | 0.13.2 | Correlation heatmaps |
| `geopandas` | 1.1.1 | Choropleth maps (`map.py`, `maps_all.py`) |

Install everything with:

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

`geopandas` pulls in `shapely`, `pyproj`, and `pyogrio` automatically; on some systems these need system-level GDAL/GEOS libraries. If `pip install` fails on `geopandas`, install it via `conda`/`mamba` or your OS package manager first, then reinstall the rest with pip.

### 🗄️ Database Configuration

**health-data-client has no database of its own.** All analysis here reads data exclusively through the REST API exposed by [`health-data-etl`](https://github.com/izabelnascimento/health-data-etl), which is the component responsible for the PostgreSQL-backed Refined Zone of the HERO architecture.

Before running anything in this repository:

1. Clone and set up `health-data-etl` following its own README (database creation, migrations, and its environment variables are configured there, not here).
2. Start the `health-data-etl` service. By default, these scripts expect it at `http://localhost:8080`.
3. Only then run the scripts in this repository — they simply query that running API.

### 🔧 Configuration

There are currently **no OS environment variables** used by this repository. Each script instead defines its own configuration as plain constants at the top of the file, for example:

```python
BASE_URL = "http://localhost:8080/api/dea/indicators/first-semester/ranked?year={year}&rank={rank}"
YEARS = [2021, 2022, 2023, 2024, 2025]
OUTPUT_DIR = "resources/v2/ranked"
RANK = 10
```

To point a script at a different `health-data-etl` instance, change the host in its `BASE_URL` constant directly. To change the analyzed period or how many top/bottom municipalities are shown, edit `YEARS` and `RANK` the same way. This is a known limitation (no centralized/env-based configuration yet) — see [Known quirks](#-known-quirks) below.

### ▶️ Running the Scripts

Every script is standalone (`python src/<script>.py`) and requires `health-data-etl` to be running. **Pay attention to the working directory** — the scripts are not all consistent about it: some resolve their output path relative to `src/` (so they must be run from inside `src/`), others relative to the repository root.

| Script | What it generates | Run from | Output |
| --- | --- | --- | --- |
| `dea_indicator.py` | Efficiency-by-city line chart (legacy, one year) | `src/` | `resources/v1/all/` |
| `dea_indicator_ranked.py` | Top/Bottom ranked efficiency, one PNG per year | `src/` | `resources/v2/ranked/` |
| `dea_indicator_ranked_all.py` | Top/Bottom ranked efficiency, all years combined | repo root | `resources/v2/ranked/` |
| `dea_indicator_ranked_redistributed.py` | Real vs. redistributed efficiency comparison | `src/` | `resources/v1/ranked/` |
| `dea_indicator_ranked_scatter.py` | Budget-per-capita vs. productivity scatter | anywhere (path is anchored to the script's own location) | `resources/v2/scatter/` |
| `correlation.py` | Correlation heatmap, one PNG per year | `src/` | `resources/v2/correlation/` |
| `correlation_all.py` | Correlation heatmaps, all years combined | `src/` | `resources/v2/correlation/` |
| `map.py` | Spatial efficiency map (legacy, per year) | `src/` | `resources/v1/map/` |
| `maps_all.py` | Spatial efficiency map, all years combined | repo root | `resources/v2/map/` |
| `productivity.py` | One-off productivity bar chart (2023) | repo root | current working directory |

Example:

```bash
# a script that expects to run from src/
cd src
python correlation.py

# a script that expects to run from the repo root
cd ..
python src/dea_indicator_ranked_all.py
```

If a script's output folder looks empty after running it, the most likely cause is running it from the wrong directory (check the table above) — it will silently create a new, unexpected `resources/` folder next to itself rather than raising an error.

### 🐛 Known Quirks

- **No `requirements.txt` before this update** — dependencies previously only existed implicitly in the local `.venv`; now tracked in [`requirements.txt`](requirements.txt).
- **Inconsistent relative paths** — as described in the table above, some scripts assume they run from `src/`, others from the repository root. `dea_indicator_ranked_scatter.py` was fixed to anchor its output path to its own file location regardless of the working directory; the rest still depend on the run directory.
- **`maps_all.py`** writes its output to `resources/v2/map/map_all_years.png` but only `os.makedirs`'s `resources/v1/map` (a leftover from an earlier version) — it currently works only because `resources/v2/map/` already exists in the repository.
- All scripts require `health-data-etl` to be reachable at the URL hardcoded in their `BASE_URL`/`BASE_URL_CITY`/`BASE_URL_EFF` constants; there is no offline/mocked mode.

### 🔗 Data Sources

The data used in the analysis are originally collected from:
- SIOPS (Public Health Budget Information System): http://siops.datasus.gov.br/filtro_rel_ges_dt_municipal.php  
- SISAB (Primary Health Care Information System): https://sisab.saude.gov.br/paginas/acessoRestrito/relatorio/federal/saude/RelSauProducao.xhtml  
- e-Gestor APS: https://relatorioaps.saude.gov.br/cobertura/aps  

### 📄 Related Publication

This analytical pipeline is part of the HERO architecture validation and is based on previous research:

- SBSI 2025 (SmartAPSUS project context): https://sol.sbc.org.br/index.php/sbsi/article/view/34367
- SBCAS 2025 (DEA proof of concept): https://sol.sbc.org.br/index.php/sbcas/article/view/35541
- SBSI 2026 (Primary Healthcare Efficiency Indicators): not available yet

🔗 Repository: https://github.com/izabelnascimento/health-data-client
