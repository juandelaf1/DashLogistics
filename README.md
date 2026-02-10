# 🚢 DashLogistics Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)](https://streamlit.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

![DashLogistics Banner](https://copilot.microsoft.com/th/id/BCO.41ecb967-dd6c-47b5-931b-b59f26cd1e80.png)

> **Sistema completo de Business Intelligence para análisis de eficiencia logística y optimización de rutas basado en datos demográficos, climáticos y de combustible.**

## 🎯 **Visión del Proyecto**

DashLogistics es una plataforma de **Data Intelligence** que combina múltiples fuentes de datos para proporcionar insights accionables sobre eficiencia logística en Estados Unidos. El proyecto demuestra capacidades end-to-end de **Data Engineering** y **Data Science**:

- **ETL Pipeline** automatizado con validación robusta
- **Data Enrichment** mediante APIs externas (combustible, clima)
- **Machine Learning** para predicciones de eficiencia
- **Dashboard interactivo** con visualizaciones en tiempo real
- **Arquitectura escalable** con Docker y PostgreSQL

## 🏗️ **Arquitectura del Sistema**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   ETL Pipeline   │    │   Data Storage  │
│                 │    │                  │    │                 │
│ • Kaggle Dataset│───▶│ • Data Cleaning  │───▶│ • PostgreSQL    │
│ • Fuel API      │    │ • Validation     │    │ • Master Tables │
│ • Weather API   │    │ • Enrichment     │    │ • Versioning    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌──────────────────┐           │
│   ML Models     │    │   Dashboard      │◀──────────┘
│                 │    │                  │
│ • Linear Reg.   │    │ • Streamlit      │
│ • KPI Analysis  │    │ • Plotly Viz     │
│ • Predictions   │    │ • Real-time      │
└─────────────────┘    └──────────────────┘
```

## 🚀 **Características Principales**

### 📊 **ETL Pipeline Avanzado**
- **Validación de datos** con Pydantic schemas
- **Logging estructurado** con run_id único para trazabilidad
- **Manejo robusto de errores** y reintentos automáticos
- **Procesamiento idempotente** con SQLAlchemy

### 🌤️ **Data Enrichment**
- **Precios de combustible**: Scraping automatizado de AAA
- **Datos climáticos**: WeatherAPI.com + OpenWeather fallback
- **Integración inteligente** con detección de outliers

### 🤖 **Machine Learning**
- **Modelos predictivos** de eficiencia logística
- **Análisis de correlación** entre variables
- **Métricas de evaluación** automáticas

### 📈 **Dashboard Interactivo**
- **KPIs en tiempo real** de eficiencia
- **Análisis geográfico** por estados
- **Visualizaciones interactivas** con Plotly
- **Modelado predictivo** integrado

## 🛠️ **Stack Tecnológico**

| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| **Backend** | Python 3.11+ | Core ETL y ML |
| **Base de Datos** | PostgreSQL 15 | Almacenamiento principal |
| **Dashboard** | Streamlit + Plotly | Visualización interactiva |
| **APIs** | WeatherAPI, OpenWeather | Enriquecimiento de datos |
| **Scraping** | BeautifulSoup + Requests | Datos de combustible |
| **Validación** | Pydantic | Calidad de datos |
| **Testing** | pytest | Calidad del código |
| **Container** | Docker + Docker Compose | Despliegue consistente |
| **Calidad** | Ruff, pre-commit | Linting y formateo |

## 📋 **Requisitos Previos**

- **Python 3.11+**
- **PostgreSQL 15+** (o Docker)
- **Git** para clonar el repositorio

## ⚙️ **Instalación y Configuración**

### 1. **Clonar el Repositorio**
```bash
git clone https://github.com/juandelaf1/DashLogistics.git
cd DashLogistics
```

### 2. **Entorno Virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

### 3. **Dependencias**
```bash
pip install -r requirements.txt
```

### 4. **Variables de Entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones:
# DATABASE_URL=postgresql://user:pass@localhost:5432/shipping_db
# WEATHERAPI_KEY=tu_api_key
# OPENWEATHER_API_KEY=tu_api_key_opcional
```

### 5. **Base de Datos**
```bash
# Opción A: Docker (recomendado)
docker-compose up -d db

# Opción B: PostgreSQL local
# Crear database 'shipping_db' y configurar conexión en .env
```

## 🚀 **Ejecución del Sistema**

### **Modo Desarrollo**
```bash
# 1. Ejecutar pipeline ETL completo
python main.py

# 2. Iniciar dashboard
streamlit run dashboard/dashboard.py
```

### **Modo Producción (Docker)**
```bash
# Todos los servicios
docker-compose up -d

# Acceso:
# Dashboard: http://localhost:8501
# API: http://localhost:5000
# Base de datos: localhost:5432
```

## 📊 **Uso del Dashboard**

### **Páginas Disponibles:**

1. **🏠 Dashboard Principal**
   - KPIs de eficiencia logística
   - Análisis de correlación población-ranking
   - Top/Bottom estados por eficiencia

2. **📈 Análisis Predictivo**
   - Modelos de Machine Learning
   - Métricas de evaluación
   - Visualizaciones predictivas

3. **⛽ Precios Combustible**
   - Análisis de precios por estado
   - Correlación con eficiencia logística
   - Tendencias y variaciones

4. **🌤️ Impacto Climático**
   - Datos meteorológicos en tiempo real
   - Análisis de impacto en operaciones
   - Mapas de calor climáticos

## 🧪 **Testing**

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=src

# Tests específicos
pytest tests/test_etl.py
pytest tests/test_logging.py
```

## 📁 **Estructura del Proyecto**

```
DashLogistics/
├── src/                          # Código fuente principal
│   ├── etl/                     # Lógica ETL
│   │   ├── etl.py              # Pipeline principal
│   │   ├── scrapers/           # Web scraping
│   │   └── enrichment/         # APIs externas
│   ├── database/                # Configuración BD
│   ├── utils/                   # Utilidades
│   └── api/                     # Endpoints (futuro)
├── dashboard/                    # Streamlit dashboard
├── tests/                        # Suite de pruebas
├── alembic/                      # Migraciones BD
├── archive/                      # Código legacy
├── logs/                         # Logs del sistema
└── docker-compose.yml           # Orquestación
```

## 🔧 **Configuración Avanzada**

### **API Keys**
- **WeatherAPI.com** (recomendado): 1M llamadas/mes gratis
- **OpenWeather**: 60 llamadas/minuto gratis
- Configurar ambas para fallback automático

### **Base de Datos**
- **Producción**: Configurar connection pooling
- **Testing**: Base de datos separada
- **Backups**: Automatizados con pg_dump

### **Logging**
- **Niveles**: DEBUG, INFO, WARNING, ERROR
- **Destinos**: Archivo rotativo + consola
- **Trazabilidad**: run_id único por ejecución

## 📈 **Métricas y KPIs**

### **KPIs Principales:**
- **Índice Eficiencia**: `population_per_rank`
- **Costo-eficiencia**: `pop_per_dollar`
- **Impacto climático**: correlación temperatura-eficiencia
- **Variabilidad**: desviación estándar por región

### **Modelos ML:**
- **Regresión Lineal**: predicción de ranking
- **R² Score**: evaluación de ajuste
- **MSE**: error cuadrático medio

## 🚀 **Roadmap Futuro**

### **Short Term (Próximas 2 semanas)**
- [ ] Integrar más variables climáticas
- [ ] Añadir tests de integración
- [ ] Optimizar queries de base de datos

### **Medium Term (Próximo mes)**
- [ ] API REST completa con FastAPI
- [ ] Sistema de alertas automáticas
- [ ] Integración con más datasets

### **Long Term (Próximos 3 meses)**
- [ ] Machine Learning avanzado (Random Forest, XGBoost)
- [ ] Sistema de recomendación de rutas
- [ ] Dashboard móvil responsive

## 🤝 **Contribuciones**

Las contribuciones son bienvenidas. Por favor:

1. Fork del repositorio
2. Crear feature branch (`git checkout -b feature/amazing-feature`)
3. Commit cambios (`git commit -m 'Add amazing feature'`)
4. Push al branch (`git push origin feature/amazing-feature`)
5. Abrir Pull Request

## 📝 **Licencia**

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👨‍💻 **Autor**

**Juan M. de la Fuente Larrocca**
- Data Analyst & Data Engineer
- Madrid, España
- [GitHub](https://github.com/juandelaf1)
- [LinkedIn](https://linkedin.com/in/juandelaf1)

## 🙏 **Agradecimientos**

- **Kaggle** por datasets demográficos
- **WeatherAPI.com** por API climática generosa
- **AAA** por datos de precios de combustible
- **Streamlit** por framework de dashboard increíble

---

<div align="center">

**🚢 DashLogistics - Transformando datos en inteligencia logística 🚢**

*Built with ❤️ using Python, Streamlit & PostgreSQL*

</div>
