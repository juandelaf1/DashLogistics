# DashLogistics

Logistics data/analytics experiment: US freight data pipeline (ETL enrichment) + dashboard (Streamlit) for exploring routes, states and cost components.

> **Estado (honesto):** proyecto de ingeniería de datos/exploración. El “modelo ML” actual **no es predictivo sobre costes observados**; es un ajuste sobre un coste derivado determinísticamente (ver abajo). No apto para decisiones operativas reales sin reconstrucción con tarifas/costes reales.

## Qué contiene (verificado en `data/dashlogistics.db`)
- `state_shipping`: **50 estados**; `state_routes`: **625 rutas**; `route_costs`: **625** con `driving_mi, driving_hr, fuel_cost, driver_cost, maint_cost, total_cost, diesel_price, fuel_pct`.
- Pipeline/enriquecimiento en `src/` (rutas/costes, congestión, freight lanes/modos/commodities, combustible, clima, etc.) y dashboard Streamlit.

## “Cost prediction” — realidad (E3 audit)
- `src/analysis/cost_estimator.py` calcula `total_cost = fuel_cost + driver_cost + maint_cost` de forma **determinística** desde distancia/tiempo (y componentes de precio), p. ej. `fuel=(mi/MPG)*diesel`, `driver=hr*rate`, `maint=mi*rate`.
- `src/analysis/cost_predictor.py` entrena `LinearRegression` para predecir `total_cost` usando solo `["driving_mi","driving_hr"]` sobre ese mismo coste derivado.
- Métricas **almacenadas** (`ml_metrics`): R²=**0.9873**, MAE=**$82.41**, RMSE=**$132.62** (n_train=500, n_test=125). Coefs: intercept -27.19, `driving_mi` 1.829, `driving_hr` **-6.947** (coeficiente negativo = artefacto de multicolinealidad/ajuste a un objetivo derivado). Correlaciones `total_cost~driving_mi`≈0.9933, `~driving_hr`≈0.9918.
- **Interpretación:** R² alto aquí mide *recuperación de una fórmula conocida*, no capacidad predictiva sobre costes reales de mercado. Para predicción real se requieren tarifas/costes observados (p. ej. FAF/APIs de rates) y validación no circular.

## Stack (real)
Python, Pandas, Streamlit, Plotly, scikit-learn, SQLAlchemy. **Almacenamiento actual: SQLite** (`data/dashlogistics.db`); PostgreSQL/Docker/dbt aparecen como aspiracionales/parciales — verificar antes de afirmarlo como operativo.

## Limitaciones
- Coste derivado determinísticamente (no tarifas reales observadas) → métrica R² **no** evidencia predicción real.
- Datos públicos; sin precios spot en tiempo real ni disrupciones en vivo.
- Revisar KPI/duplicados en cualquier vista agregada antes de citar cifras de negocio.

---
*E3 audit (2026-11-08): narrativa/claims alineados con evidencia. El case study enlazado externamente puede requerir actualización para no afirmar R²=0.987 como accuracy predictiva.*