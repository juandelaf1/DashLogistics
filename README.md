# 🚢 DashLogistics Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)](https://streamlit.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

![DashLogistics Banner](https://copilot.microsoft.com/th/id/BCO.b36c81a5-ec44-4e05-bbd1-e49c43035b21.png)

<h3 align="center">
Business Intelligence project focused on logistics efficiency analysis
</h3>

---

## 📑 Table of Contents

- [Project Vision](#-project-vision)
- [System Architecture](#-system-architecture)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Running the Project](#-running-the-project)
- [Dashboard Overview](#-dashboard-overview)
- [Testing](#-testing)
- [Project Structure](#-project-structure)
- [Key KPIs](#-key-kpis)
- [Future Improvements](#-future-improvements)
- [Author](#-author)
  
---

## 🎯 Project Vision

DashLogistics is a data analytics platform designed to explore how different factors such as population, fuel prices, and weather conditions impact logistics efficiency.

The project demonstrates an end-to-end analytics workflow, including:

- ETL pipeline for data ingestion and cleaning
- Data enrichment using external APIs
- Exploratory analysis and KPI evaluation
- Machine learning models for predictive insights
- Interactive dashboard for data visualization

The goal is to show how data can support logistics decision-making and operational efficiency analysis.

---

## 📂 Data Sources

The project integrates multiple data sources to analyze logistics efficiency:

- **Logistics dataset** from Kaggle
- **Fuel price data** collected via web scraping
- **Weather data** retrieved through external APIs
- **Demographic data** for population analysis

These datasets are processed through an ETL pipeline before being stored in PostgreSQL.

---

## 🏗️ System Architecture


```text
Data Sources
     ↓
ETL Pipeline
     ↓
PostgreSQL Database
     ↓
Analysis & ML Models
     ↓
Streamlit Dashboard
```

### Main components

**Data Sources**

- Kaggle logistics datasets
- Fuel price data
- Weather APIs

**ETL Pipeline**

- Data cleaning
- Validation
- Data enrichment

**Database**

- PostgreSQL for structured storage

**Analysis & ML**

- Correlation analysis
- Predictive models

**Dashboard**

- Streamlit + Plotly visualizations

---

## 🚀 Key Features

### 📊 Data Pipeline

- Automated data extraction and transformation
- Data validation and cleaning
- Integration of multiple datasets

### 🌤️ Data Enrichment

- Fuel price data
- Weather information
- Regional demographic data

### 🤖 Predictive Analysis

Explore relationships between:

- Population density
- Logistics ranking
- Fuel prices
- Weather conditions

### 📈 Interactive Dashboard

The dashboard allows users to:

- Explore logistics efficiency KPIs
- Analyze geographic patterns
- Visualize correlations between variables
- Explore predictive model outputs

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Programming | Python 3.11 | Data processing |
| Data Analysis | Pandas, NumPy | Data manipulation |
| Database | PostgreSQL | Data storage |
| Visualization | Plotly | Interactive charts |
| Dashboard | Streamlit | Data app |
| APIs | WeatherAPI, OpenWeather | External data |
| Web Scraping | BeautifulSoup | Fuel price data |
| Environment | Docker | Deployment |

---

## 📋 Requirements

- Python 3.11+
- PostgreSQL 15+ (optional if using Docker)
- Git

---

## ⚙️ Installation

### Clone repository

```bash
git clone https://github.com/juandelaf1/DashLogistics.git
cd DashLogistics
```

### Create virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Project

### Run the ETL pipeline

```bash
python main.py
```

### Start the dashboard

```bash
streamlit run dashboard/dashboard.py
```

Dashboard will be available at:

```
http://localhost:8501
```

---

## 📊 Dashboard Overview

### 🏠 Main Dashboard

- Logistics efficiency KPIs
- Population vs logistics ranking
- Top and bottom states by efficiency

### 📈 Predictive Analysis

- Machine learning models
- Evaluation metrics
- Predictive visualizations

### ⛽ Fuel Price Analysis

- State-level fuel price comparisons
- Impact on logistics efficiency

### 🌤️ Weather Impact

- Weather conditions analysis
- Relationship between climate and logistics performance

---

## 🧪 Testing

Run tests using:

```bash
pytest
```

With coverage:

```bash
pytest --cov=src
```

---

## 📁 Project Structure

```bash
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
```

---

## 📈 Key KPIs

- Logistics efficiency index
- Population per logistics rank
- Fuel cost efficiency
- Weather impact correlations

---

## 🔮 Future Improvements

- Add more weather and traffic variables
- Improve predictive models
- Include route optimization simulations
- Deploy dashboard in the cloud
- Expand dataset coverage

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
