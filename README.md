# 🚢 DashLogistics Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)](https://streamlit.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

![DashLogistics Banner](https://copilot.microsoft.com/th/id/BCO.b36c81a5-ec44-4e05-bbd1-e49c43035b21.png)

> **Business Intelligence project focused on logistics efficiency analysis and route optimization using demographic, fuel and weather data.**

---

# 🎯 Project Vision

DashLogistics is a **data analytics platform** designed to explore how different factors such as **population, fuel prices and weather conditions** impact logistics efficiency.

The project demonstrates an **end-to-end analytics workflow**, including:

- **ETL pipeline** for data ingestion and cleaning  
- **Data enrichment** using external APIs  
- **Exploratory analysis and KPI evaluation**  
- **Machine learning models for predictive insights**  
- **Interactive dashboard** for data visualization  

The goal is to show how **data can support logistics decision-making and operational efficiency analysis**.

---

# 🏗️ System Architecture

Data Sources → ETL Pipeline → Database → Analysis & ML → Dashboard


Main components:

- **Data Sources**
  - Kaggle logistics datasets
  - Fuel price data
  - Weather APIs

- **ETL Pipeline**
  - Data cleaning
  - Validation
  - Data enrichment

- **Database**
  - PostgreSQL for structured storage

- **Analysis & ML**
  - Correlation analysis
  - Predictive models

- **Dashboard**
  - Streamlit + Plotly visualizations

---

# 🚀 Key Features

### 📊 Data Pipeline

- Automated **data extraction and transformation**
- Data validation and cleaning
- Integration of multiple datasets

### 🌤️ Data Enrichment

External data sources used to enrich the analysis:

- Fuel price data
- Weather information
- Regional demographic data

### 🤖 Predictive Analysis

Basic predictive modeling to explore relationships between variables such as:

- population density
- logistics ranking
- fuel prices
- weather conditions

### 📈 Interactive Dashboard

The dashboard allows users to:

- Explore logistics efficiency KPIs
- Analyze geographic patterns
- Visualize correlations between variables
- Explore predictive model outputs

---

# 🛠️ Tech Stack

| Component | Technology | Purpose |
|------------|------------|-----------|
| **Programming** | Python 3.11 | Data processing |
| **Data Analysis** | Pandas, NumPy | Data manipulation |
| **Database** | PostgreSQL | Data storage |
| **Visualization** | Plotly | Interactive charts |
| **Dashboard** | Streamlit | Data app |
| **APIs** | WeatherAPI, OpenWeather | External data |
| **Web Scraping** | BeautifulSoup | Fuel price data |
| **Environment** | Docker | Deployment |

---

# 📋 Requirements

- Python 3.11+
- PostgreSQL 15+ (optional if using Docker)
- Git

---

# ⚙️ Installation

### Clone repository

```bash
git clone https://github.com/juandelaf1/DashLogistics.git
cd DashLogistics

Create virtual environment

python -m venv venv
source venv/bin/activate

Windows:

venv\Scripts\activate

Install dependencies

pip install -r requirements.txt

🚀 Running the Project
Run the ETL pipeline

python main.py

Start the dashboard

streamlit run dashboard/dashboard.py

Dashboard will be available at:

http://localhost:8501

📊 Dashboard Overview
🏠 Main Dashboard

Logistics efficiency KPIs

Population vs logistics ranking

Top and bottom states by efficiency

📈 Predictive Analysis

Machine learning models

Evaluation metrics

Predictive visualizations

⛽ Fuel Price Analysis

State-level fuel price comparisons

Impact on logistics efficiency

🌤️ Weather Impact

Weather conditions analysis

Relationship between climate and logistics performance

🧪 Testing

Run tests using:

pytest

With coverage:

pytest --cov=src

📁 Project Structure

DashLogistics/
├── src/
│   ├── etl/
│   ├── database/
│   ├── utils/
│   └── api/
├── dashboard/
├── tests/
├── logs/
├── archive/
└── docker-compose.yml

📈 Key KPIs

Main metrics analyzed in the project:

Logistics efficiency index

Population per logistics rank

Fuel cost efficiency

Weather impact correlations

🔮 Future Improvements

Potential next steps:

Add more weather and traffic variables

Improve predictive models

Include route optimization simulations

Deploy dashboard in the cloud

Expand dataset coverage

👨‍💻 Author

Juan Manuel de la Fuente Larrocca

Data Analyst
Madrid, Spain

GitHub
https://github.com/juandelaf1

LinkedIn
https://linkedin.com/in/juandelafuentelarrocca

<div align="center">

🚢 DashLogistics — Turning logistics data into actionable insights

</div> ```
