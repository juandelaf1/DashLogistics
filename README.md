# 🚢 DashLogistics — Logistics Intelligence Pipeline

[![CI](https://img.shields.io/github/actions/workflow/status/juandelaf1/DashLogistics/ci.yml?branch=master&label=CI&logo=github)](https://github.com/juandelaf1/DashLogistics/actions)
[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-17%2F17-brightgreen)](tests/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red?logo=streamlit)](https://streamlit.io)
[![Pandas](https://img.shields.io/badge/Pandas-3.x-blue?logo=pandas)](https://pandas.pydata.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> End-to-end ETL pipeline that transforms public logistics data into business intelligence: demographics, fuel prices, and weather — enriched with KPIs, interactive maps, and a live dashboard.

---

## Dashboard Preview

| Population | Efficiency | Fuel |
|:---:|:---:|:---:|
| ![Population](docs/images/population_map.png) | ![Efficiency](docs/images/efficiency_map.png) | ![Diesel](docs/images/diesel_map.png) |
| **Freight Opportunity** | **Demand vs Cost** | **Correlations** |
| ![Freight Opportunity](docs/images/freight_opportunity_map.png) | ![Demand vs Cost](docs/images/demand_vs_cost.png) | ![Correlation](docs/images/correlation_heatmap.png) |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.13 |
| Data | Pandas 3.x + SQLAlchemy + SQLite/PostgreSQL |
| Scraping | Requests + BeautifulSoup |
| Validation | Pydantic v2 |
| Dashboard | Streamlit + Plotly |
| Testing | pytest (17 tests) |
| CI/CD | GitHub Actions |

---

## Quick Start

```bash
git clone https://github.com/juandelaf1/DashLogistics.git
cd DashLogistics
pip install -r requirements.txt
python main.py                         # Run full pipeline
streamlit run dashboard/dashboard.py   # Launch dashboard
```

**No PostgreSQL required** — the pipeline defaults to SQLite. Set `DATABASE_URL` in `.env` if you have PostgreSQL.

---

## Pipeline

```
shipping_data.csv (52 states)
       │
       ▼
  ETL ──► clean + validate (Pydantic) ──► shipping_stats (SQLite/PG)
       │
       ▼
  AAA fuel scraper ──► fuel_prices (50 states, live prices)
       │
       ▼
  OpenWeatherMap ──► weather_data (temp, humidity, wind)
       │
       ▼
  Enriched dataset ──► data/final/enriched_data.csv (50 rows × 15 cols)
       │
       ▼
  KPIs + Features ──► freight_opportunity_score, efficiency_tiers, regions
```

### Run

```bash
python main.py
```

Output:
```
▶ Step 1: Downloading raw data...
▶ Step 2: Running ETL (clean & validate)...   50 valid states
▶ Step 3: Scraping fuel prices...             50 AAA price records
▶ Step 4: Enriching with weather data...      50 OpenWeatherMap records
▶ Step 5: Creating final enriched dataset...  50 rows × 15 columns
✅ PIPELINE COMPLETED SUCCESSFULLY
```

---

## Tests

```bash
pytest -v    # 17/17 passing
```

Covers: ETL (cleaning, validation), scraper (fuel), KPIs (basic, efficiency, composite), feature engineering, logging (RunIdFormatter/Filter), pipeline integration, and edge cases (empty DataFrames).

---

## Project Structure

```
src/
├── etl/              # Pipeline: etl.py, scrapers/, enrichment/
│   ├── enrichment/   # weather_api.py (OpenWeatherMap)
│   └── scrapers/     # fuel_scraper.py (AAA gas prices)
├── database/         # db.py (SQLite fallback + pandas 3.x helpers)
├── analysis/         # kpis.py (15 metrics), features.py
├── utils/            # state_mapper.py, download_data.py
└── visualization/    # charts.py
dashboard/            # dashboard.py (Streamlit)
tests/                # 17 tests
data/                 # raw/ → clean/ → final/
```

---

## Generated KPIs (15 metrics)

| Group | Metrics |
|-------|---------|
| Basic | total_states, total_population, avg_population, max/min_population, population_std, top/bottom_state |
| Efficiency | avg_efficiency_score, efficiency_score (per state), efficiency_percentile, efficiency_tier |
| Fuel | fuel_cost_index, avg_diesel, avg_regular |
| Advanced | freight_opportunity_score, logistics_demand_score, cost_efficiency_index |

---

## Data Sources

- **Population**: US Census 2014 (Plotly dataset, 52 states)
- **Fuel**: AAA Gas Prices (live web scraping, 50 states)
- **Weather**: OpenWeatherMap (50 states, ~30s runtime)
- **Output**: CSV in `data/final/` + SQLite DB (`dashlogistics.db`)

---

## Roadmap

- [x] ETL pipeline (no PostgreSQL dependency)
- [x] Interactive dashboard with maps + KPIs
- [x] Resilient fuel scraper (real User-Agent, graceful degradation)
- [x] Weather enrichment (OpenWeatherMap, functional)
- [x] 17 passing tests, green CI
- [ ] Historical fuel price tracking
- [ ] Logistics efficiency prediction model
- [ ] Cloud deployment (Streamlit Cloud)
- [ ] SkyCast integration (climate module)

---

## Author

**Juan de la Fuente** — [@juandelaf1](https://github.com/juandelaf1) — [LinkedIn](https://linkedin.com/in/juandelafuentelarrocca)

<p align="center">🚢 <b>DashLogistics</b> — logistics data, real decisions</p>
