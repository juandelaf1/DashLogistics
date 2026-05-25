# 🚢 DashLogistics: Data Analysis Pipeline

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50+-red.svg)](https://streamlit.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://postgresql.org)
[![Tests](https://img.shields.io/badge/Tests-3%2F3-brightgreen.svg)](tests/)
[![Status](https://img.shields.io/badge/Status-MVP-orange.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

<h3 align="center">
📊 End-to-End ETL + Data Analysis Pipeline for Logistics Intelligence
</h3>

> **Portfolio Project**: Demonstrating Data Engineering, Data Analysis, and Business Intelligence skills through a production-ready pipeline that combines multiple data sources, validates quality, and delivers actionable insights.

---

## 📑 Contents

- [Overview](#-overview)
- [What's Included](#-whats-included)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [Data Pipeline](#-data-pipeline)
- [Dashboard](#-dashboard)
- [Testing](#-testing)
- [Project Structure](#-project-structure)
- [Skills Demonstrated](#-skills-demonstrated)
- [Author](#-author)

---

## 🎯 Overview

**DashLogistics** is a data intelligence platform that analyzes logistics efficiency by correlating population demographics, fuel costs, and weather patterns across US states.

### What This Project Demonstrates

✅ **Data Engineering**: ETL pipeline with validation, normalization, and enrichment  
✅ **Data Analysis**: KPI development, trend analysis, correlation studies  
✅ **Business Intelligence**: Interactive dashboards with real-time metrics  
✅ **Code Quality**: Production-grade Python (Pydantic, pytest, logging)  
✅ **Database Design**: Schema planning, SQL queries, data lineage  
✅ **Problem Solving**: Handles missing data, API failures, format inconsistencies  

---

## ✅ What's Included

**MVP Status**: Production-ready analytics pipeline ✅

- ✅ **ETL Pipeline**: Load → Clean → Validate → Normalize → Enrich (50/50 states, ~5s execution)
- ✅ **Data Sources**: Demographics CSV + AAA fuel prices (real-time web scraping)
- ✅ **State Mapper**: Centralized state code normalization (`src/utils/state_mapper.py`)
- ✅ **CSV Exports**: 
  - `enriched_data.csv` (50 rows × 10 cols: shipping + fuel)
  - `logistics_analysis_enriched.csv` (50 rows × 12 cols: includes efficiency scores)
- ✅ **PostgreSQL**: shipping_stats + fuel_prices tables with audit trail (run_id tracking)
- ✅ **Jupyter Analysis**: Complete notebook (9 sections, 23 cells, 6+ visualizations)
- ✅ **Tests**: 3/3 core tests passing (ETL, scrapers, data validation)
- 🎯 **Efficiency Tiers**: States ranked by population/fuel cost ratio in 4 tiers
- ⏳ **Weather API**: Optional (graceful degradation if unavailable)

---

## 🏗️ Architecture

```
Raw Data (52 states)  →  ETL  →  Enrichment  →  Final Dataset  →  Dashboard
[CSV]               [Clean] [Scrape+Merge] [CSV+PostgreSQL]   [Streamlit]
```

**Data Pipeline Stages**:
1. **Load**: `data/raw/shipping_data.csv` → 52 US states
2. **Clean**: Normalize columns, trim whitespace, remove duplicates
3. **Validate**: Pydantic schemas enforce data quality
4. **Normalize**: State names → codes (California → CA) via `state_mapper.py`
5. **Enrich**: AAA fuel price scraping, join on state code
6. **Export**: CSV (`data/final/enriched_data.csv`) + PostgreSQL
7. **Visualize**: Streamlit dashboard with real-time KPIs

**Technical Highlights**:
- ✅ **Centralized State Mapper** (`src/utils/state_mapper.py`): Single source of truth
- ✅ **Idempotent Pipeline**: Safe to re-run without duplication
- ✅ **Error Resilience**: Optional features don't break core pipeline
- ✅ **Audit Trail**: UUID-tracked execution lineage

**Analysis & Insights**

- 📊 **Jupyter Notebook** (`notebooks/01_LOGISTICS_ANALYSIS_REPORT.ipynb`):
  - Fuel price analysis: regional trends, Top/Bottom states, price spreads
  - Population demographics: correlation analysis (0.48 with diesel prices)
  - Efficiency metrics: 4-tier classification (Top/Mid/Low/Bottom performers)
  - Regional breakdown: Northeast/South/Midwest/West comparisons
  - Executive summary: 6 actionable recommendations for logistics optimization
  - Output: `logistics_analysis_enriched.csv` with efficiency scores & tiers

- 📈 **Streamlit Dashboard** (`dashboard/dashboard.py`): 
  - Real-time KPIs and interactive Plotly visualizations
  - Geographic choropleth maps
  - Drill-down filtering and correlation analysis charts

---

## 🚀 Key Features

### 📊 **Data Pipeline** (`src/etl/`)
- ✅ Load & parse CSV data
- ✅ Pydantic validation (enforces data types & constraints)
- ✅ Automatic state code normalization (California → CA)
- ✅ Deduplication & null handling
- ✅ Computed metrics (population_per_rank)

### 🌐 **Real-Time Data Enrichment** (`src/etl/enrichment/`, `src/etl/scrapers/`)
- ✅ AAA fuel price scraping (50 states)
- ✅ Optional weather API integration
- ✅ Smart merging on state codes
- ✅ Error resilience (optional features don't block pipeline)

### 🗂️ **Dual Storage** (CSV + PostgreSQL)
- ✅ CSV exports for easy sharing/BI tools
- ✅ PostgreSQL for structured queries
- ✅ Data lineage tracking (run_id)

### 📈 **Interactive Dashboard** (`dashboard/dashboard.py`)
- ✅ Real-time KPIs (state count, population, efficiency)
- ✅ Geographic visualization (choropleth maps)
- ✅ Interactive filtering & drill-down
- ✅ Correlation analysis charts

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|----------|
| **Language** | Python 3.11+ | Core & pipelines |
| **Data Processing** | Pandas | DataFrames, transformations |
| **Validation** | Pydantic v2 | Schema enforcement |
| **Database** | PostgreSQL 15 | Data persistence |
| **ORM** | SQLAlchemy 2.0 | Database abstraction |
| **Scraping** | BeautifulSoup + Requests | Web data extraction |
| **Visualization** | Plotly | Interactive charts |
| **Dashboard** | Streamlit | Data application |
| **Testing** | pytest | Unit & integration tests |

---

## 📋 Requirements

- **Python 3.11+**
- **PostgreSQL 15+** (running locally on port 5432)
- Git

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/juandelaf1/DashLogistics.git
cd DashLogistics
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Database

```bash
# Ensure PostgreSQL is running
psql -U postgres -c "CREATE DATABASE shipping_db;"

# Tables auto-create on first pipeline run
```

### 5. Configure Environment (Optional)

Create `.env` file in root:

```env
DATABASE_URL=postgresql://postgres:admin@localhost:5432/shipping_db
WEATHERAPI_KEY=your_api_key  # Optional: for weather enrichment
```

---

## 🚀 Running the Project

### Run the ETL Pipeline

```bash
python main.py
```

**Pipeline Flow:**
1. ✅ Download raw shipping data (`data/raw/shipping_data.csv`)
2. ✅ Clean & validate with Pydantic schemas
3. ✅ Normalize state codes (50 valid US states)
4. ✅ Scrape AAA fuel prices for all states
5. ✅ Optionally enrich with weather data
6. ✅ Generate enriched CSV (`data/final/enriched_data.csv`)
7. ✅ Load to PostgreSQL (`shipping_stats`, `fuel_prices`, `weather_data` tables)

**Output:**
- CSV: 50 rows × 10 columns (rank, state, postal, population, fuel prices, etc.)
- PostgreSQL: Normalized, queryable data
- Logs: `logs/pipeline_{timestamp}.log` (run tracking)

### Launch Dashboard

```bash
streamlit run dashboard/dashboard.py
```

Opens http://localhost:8501/ with:
- KPI cards (state count, population stats)
- Geographic heatmap
- Correlation matrix
- Raw data explorer

---

## 📊 Dashboard Overview

### 📋 KPI Overview
- Total states analyzed (50)
- Total population served
- Average efficiency metrics
- Data freshness timestamp

### 🌐 Geographic Analysis
- Interactive US choropleth by state
- Population density heatmap
- State rankings visualization

### ⛽ Fuel Price Analytics
- Regular/mid-grade/premium/diesel prices by state
- Regional price comparisons
- State pair analysis

### 📈 Data Explorer
- Raw table view (sortable/filterable)
- CSV export capability
- Custom queries

---

## ✅ Testing

### Run All Tests

```bash
pytest -v
```

**Test Coverage:**
- `test_etl.py`: Data cleaning, schema validation, state normalization
- `test_scrapers.py`: Fuel price scraping, HTML parsing, field validation
- `test_logging.py`: Run ID generation, log file creation

**Expected Result:**
```
test_etl.py::test_clean_data PASSED
test_scrapers.py::test_fuel_scraper PASSED
test_logging.py::test_run_id PASSED
======================== 5 passed in 0.23s ========================
```

### Run Specific Test

```bash
pytest tests/test_etl.py -v
pytest tests/test_scrapers.py::test_fuel_scraper -v
```

---

## 📁 Project Structure

```bash
DashLogistics/
├── src/
│   ├── etl/                      # Pipeline orchestration
│   │   ├── etl.py               # Main ETL loader
│   │   ├── enrichment/          
│   │   │   └── weather_api.py   # Optional weather enrichment
│   │   └── scrapers/
│   │       ├── fuel_scraper.py  # AAA fuel price scraper
│   │       └── update_master_data.py
│   ├── database/
│   │   ├── database.py          # SQLAlchemy engine
│   │   └── schemas.py           # Pydantic/ORM models
│   ├── utils/
│   │   ├── state_mapper.py      # ⭐ State normalization (critical)
│   │   └── download_data.py     # CSV downloader
│   └── visualization/
│       └── charts.py            # Dashboard styling & helpers
│
├── dashboard/
│   └── dashboard.py             # Streamlit app
│
├── data/
│   ├── raw/                     # Source CSV (52 states)
│   │   └── shipping_data.csv
│   └── final/                   # Enriched output
│       └── enriched_data.csv    # 50 states × 10 columns
│
├── tests/
│   ├── test_etl.py
│   ├── test_scrapers.py
│   └── test_logging.py
│
├── logs/                        # Audit trail (run_id tracking)
│
├── main.py                      # Pipeline entry point
├── requirements.txt             # Dependencies (10 packages)
├── pytest.ini                   # Test config
└── README.md                    # This file
```

---

## � Key Metrics

**Dataset Coverage:**
- 📍 50 US states (DC excluded)
- 👥 Total population: ~328M across region
- ⛽ 50 fuel price points (regular/mid/premium/diesel)
- 📈 10 data dimensions per state

**Performance Targets:**
- Pipeline runtime: ~5 seconds (full load & enrich)
- Data freshness: Real-time (on-demand runs)\n- Test coverage: 5/5 unit tests passing
- CSV generation: Automatic on each run

---

## 🔮 Future Enhancements

**Phase 2** (Post-MVP):
- ✨ Add historical fuel price trends
- ✨ Integrate real-time traffic data
- ✨ Implement weather impact analysis (requires API key)
- ✨ Time-series forecasting models
- ✨ Automated daily data refresh (cron jobs)

**Phase 3** (Production-Ready):
- 🚀 Deploy dashboard to cloud (Streamlit Cloud / AWS)
- 🚀 Add user authentication
- 🚀 Export reports to Power BI
- 🚀 Predictive modeling pipeline
- 🚀 API endpoint for third-party integrations

---

## 👨‍💻 Author

**Juan Manuel de la Fuente Larrocca**  
Data Analyst — Madrid, Spain

GitHub: [juandelaf1](https://github.com/juandelaf1)  
LinkedIn: [juandelafuentelarrocca](https://linkedin.com/in/juandelafuentelarrocca)

---

<div align="center">

🚢 **DashLogistics — Turning logistics data into actionable insights**

</div>
