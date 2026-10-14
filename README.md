# DashLogistics

Multi-market logistics intelligence platform with ML cost prediction (R-squared = 0.987).

[Full Case Study](https://juandelaf1.github.io/projects/dash-logistics)

## Overview

DashLogistics analyzes multi-market logistics operations across the US, combining public freight data with a cost prediction model. Interactive dashboards track 15+ KPIs across 50 US states and 30+ market segments.

## Key Results

- **R-squared = 0.987** cost prediction accuracy
- **15+ KPIs** tracked across markets
- **50 US states** coverage
- **Multi-page dashboard** with time-series, geospatial, and market analysis

## Stack

Python - Pandas - Streamlit - Plotly - PostgreSQL - Docker

## Limitations

- Built on public freight data (Transearch/STB), not proprietary carrier data
- Does not incorporate real-time fuel prices or weather disruptions
- Cost model relies on historical rates, not live spot pricing

---

*Detailed architecture, data pipeline, and trade-off analysis at juandelaf1.github.io/projects/dash-logistics*