<p align="center">
  <img src="docs/images/dashboard_full.png" alt="Dash Logistics Banner" width="800">
</p>

# DASH LOGISTICS — Logistics Intelligence Pipeline

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)]()
[![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)]()
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75?logo=plotly&logoColor=white)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)]()
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)]()
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikit-learn&logoColor=white)]()
[![OSRM](https://img.shields.io/badge/OSRM-Routing-008080)]()
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)]()
[![Tests](https://img.shields.io/badge/Tests-17%2F17-brightgreen?logo=pytest)]()
[![License](https://img.shields.io/badge/License-MIT-yellow)]()

> **From public data to logistics intelligence. End-to-end ETL pipeline integrating 5+ data sources with ML-powered cost prediction.**

---

## Elevator Pitch

**Problem**: Logistics companies operate with fragmented data — freight flows here, fuel prices there, routing data somewhere else. Without an integrated pipeline, calculating operating costs, identifying efficient lanes, and predicting expenses becomes manual, slow, and error-prone.

**Hypothesis**: By integrating 5+ public data sources (BTS FAF freight flows, USDA truck rates, OSRM routing, EIA fuel prices, AAA gas prices) through a modular ETL pipeline and applying ML to cost prediction, we can deliver actionable logistics intelligence that adapts to any market (US, EU, LATAM, APAC).

**Solution**: DashLogistics — a fully containerized ETL pipeline and Streamlit dashboard that ingests, models, and visualizes real US freight data. Generates **15 KPIs**, achieves **R² = 0.987** on cost prediction (MAE = $82), and is architecturally designed for portability to any region.

---

## Problem

Logistics intelligence requires integrating diverse data sources:

- **Freight volumes**: State-to-state flow data (tons, value, mode, commodity)
- **Operational costs**: Fuel prices, driver rates, maintenance per mile
- **Routing**: Distance and time between locations
- **Market rates**: Truck rates per mile by lane

Without a unified pipeline, analysts spend more time collecting data than generating insights.

## Key Metrics

| Metric | Value |
|--------|-------|
| Data Sources | **5+** (FAF, USDA, OSRM, EIA, AAA) |
| KPIs Generated | **15** |
| ML Model (Cost Prediction) | **R² = 0.987**, **MAE = $82** |
| Routes Analyzed | **625** (OSRM state-to-state) |
| Tests | **17/17** passing |
| Pipeline Steps | **8** (orchestrated in main.py) |
| Dashboard Tabs | **4** (Volumes, Costs, Routes, Deep Dive) |
| US States Covered | **50** |
| Records (FAF) | **86MB** CSV -> **10** relational tables |
| CI/CD | ruff lint -> pytest -> pip-audit |
| Infrastructure | Docker, multi-stage builds, Docker Compose |

## Solution Architecture

```
+-----------------------------------------------------------------------------+
|                           DATA INGESTION LAYER                              |
+-----------------------------------------------------------------------------+
|                                                                             |
|  BTS FAF 5.7.1 -----> CSV (86MB) ----> FAF Loader ----> 10 relational tables|
|  USDA Ag Transport ---> SODA API ----> USDA Client ----> truck_rates (263)  |
|  OSRM -----------------> Public API --> OSRM Router ----> state_routes (625) |
|  EIA ------------------> REST API ----> EIA Fetcher ----> eia_fuel_prices   |
|  AAA ------------------> Scraper -----> Fuel Parser ----> fuel_prices (50)  |
|                                                                             |
+-----------------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------------+
|                           FEATURE ENGINEERING                               |
+-----------------------------------------------------------------------------+
|                                                                             |
|  Operating Cost = fuel_cost + driver_cost + maint_cost per mile             |
|  Fuel Cost     = miles / 6.5mpg x diesel_price                              |
|  Driver Cost   = hours x $35/hr                                             |
|  Maintenance   = miles x $0.15/mi                                           |
|  Congestion    = actual_time / freeflow_time (55mph)                        |
|  Lane Efficiency = tons_per_dollar                                          |
|  Trade Balance = outbound - inbound tons per state                          |
|  ML Model      = LinearRegression predicts total_cost from driving_mi + hr  |
|                                                                             |
+-----------------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------------+
|                           VISUALIZATION LAYER                               |
+-----------------------------------------------------------------------------+
|                                                                             |
|  Streamlit Dashboard ----- 4 tabs ----- Interactive choropleth map          |
|  Port 8502                   Flow lines          Select-state drill-down    |
|                              KPI cards           USDA rate comparison       |
|                              Mode split          Cost breakdown             |
|                              Trade balance       Congestion analysis        |
|                                                                             |
+-----------------------------------------------------------------------------+
```

## Skills Demonstrated

| Skill | Implementation |
|-------|---------------|
| **ETL Pipeline Design** | Multi-stage ingestion (CSV, REST APIs, web scraping) |
| **Data Modeling** | Aggregation, derived features, trade balance, congestion proxy |
| **Cost Analytics** | Operating cost engine: fuel + driver + maintenance per route |
| **Machine Learning** | Linear regression for route cost prediction (R² = 0.987) |
| **Geospatial Analysis** | OSRM routing, state-to-state distance caching, flow maps |
| **Dashboard Engineering** | Streamlit + Plotly with interactive mapping, multi-tab UX |
| **Infrastructure** | Docker containerization, multi-stage builds, GitHub Actions CI |
| **Resilience** | SQLite fallback, graceful degradation on API failures, retry logic |

## Data Sources

| Source | Data | Access | Refresh |
|--------|------|--------|---------|
| [BTS FAF 5.7.1](https://www.bts.gov/faf) | State-to-state freight flows (tons, value, mode, commodity, 2018-2024) | Public CSV (86MB) | Semi-annual |
| [USDA Ag Transport](https://agtransport.usda.gov/) | Refrigerated truck rates per mile by lane | SODA API (free) | Quarterly |
| [OSRM](https://project-osrm.org/) | Driving distance & time between state centroids | Public routing API | On-demand |
| [EIA](https://www.eia.gov/opendata/) | Official weekly diesel & gasoline prices | REST API (free key) | Weekly |
| [AAA Gas Prices](https://gasprices.aaa.com/) | Street-level fuel prices by state | Web scraping | Daily |

**No API keys required for basic operation** — FAF, USDA, and OSRM are all public.

## Dashboard

| Tab | Content |
|-----|---------|
| **Volumes** | Trends, commodities, mode split, trade balance |
| **Costs & Congestion** | Operating cost, congestion heatmap, efficient lanes, ML cost prediction |
| **Routes by Mode** | Truck / Rail / Water flow maps |
| **Deep Dive** | State-level drill-down with all metrics |

## Quick Start

### Docker (recommended)
```bash
docker compose up -d
# Open http://localhost:8502
```

### Local
```bash
pip install -r requirements.txt
python main.py                          # Run full pipeline
streamlit run dashboard/dashboard.py    # Launch dashboard
```

## Adapting to Other Markets

| US | Europe | LATAM |
|----|--------|-------|
| BTS FAF | [Eurostat](https://ec.europa.eu/eurostat) | [INE](https://ine.gov.br) / [KAP](https://datos.gob.mx) |
| USDA | [Eurostat transport](https://ec.europa.eu/eurostat/web/transport) | Local logistics surveys |
| OSRM | OSRM (same API, global) | OSRM (same API) |
| AAA/EIA | [Fuel prices EU](https://ec.europa.eu/energy) | Local fuel authorities |

---

## Author

**Juan de la Fuente** — [@juandelaf1](https://github.com/juandelaf1)

juandelafuentelarrocca@gmail.com

MIT © 2026
