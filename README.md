# 🚢 Shipping ETL Pipeline  
Pipeline de descarga, limpieza y transformación de datos con Python

Este proyecto implementa un pipeline ETL completo utilizando Python.  
Incluye:

- Descarga automática de datos desde una URL
- Limpieza y transformación del dataset
- Logging profesional (archivo + consola)
- Orquestación del pipeline mediante `main.py`
- Estructura modular y reproducible
- Uso de entorno virtual, `.env` y `.gitignore`

Es un ejemplo claro y profesional de un flujo de trabajo típico en Data Engineering.

---

## 📁 Estructura del proyecto


shipping_etl_project/ │ ├── data/ │   ├── raw/                # Datos originales descargados │   └── clean/              # Datos procesados por el ETL │ ├── logs/ │   ├── etl.log             # Logs del proceso ETL │   └── pipeline.log        # Logs del orquestador │ ├── src/ │   ├── download_data.py    # Script de descarga │   ├── etl.py              # Script ETL con transformaciones │   └── main.py             # Orquestador del pipeline │ ├── .env                    # Variables de entorno (rutas y URL) ├── .gitignore              # Exclusiones para Git ├── requirements.txt        # Dependencias del proyecto └── README.md               # Documentación del proyecto

---

## ⚙️ Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPO>
cd shipping_etl_project


2. Crear entorno virtual
python -m venv venv
source venv/Scripts/activate   # Windows (Git Bash)


3. Instalar dependencias
pip install -r requirements.txt


4. Configurar variables de entorno
Archivo .env:
RAW_DATA_PATH=../data/raw/shipping_data.csv
CLEAN_DATA_PATH=../data/clean/shipping_data_clean.csv
DATA_URL=https://raw.githubusercontent.com/plotly/datasets/master/2014_usa_states.csv



🚀 Ejecución del pipeline completo
Desde la carpeta src/:
python main.py


Esto ejecuta:
- download_data.py → descarga el dataset
- etl.py → limpia, transforma y guarda los datos
- Logging en logs/pipeline.log y logs/etl.log

🧹 Transformaciones realizadas en el ETL
El script etl.py realiza:
- Normalización de nombres de columnas
- Limpieza de espacios en strings
- Conversión de columnas numéricas
- Eliminación de duplicados
- Eliminación de filas con valores críticos nulos
- Creación de columna derivada:
population_per_rank = population / rank
- Ordenación por población
- Logging detallado de cada paso

📝 Ejemplo de salida
Archivo generado:
data/clean/shipping_data_clean.csv


Incluye columnas limpias, tipos corregidos y métricas derivadas.

🧠 Objetivo del proyecto
Este proyecto demuestra:
- Buenas prácticas de Data Engineering
- Modularidad y separación de responsabilidades
- Uso de variables de entorno
- Logging profesional
- Orquestación de pipelines
- Reproducibilidad y claridad para recruiters
Es ideal como portfolio para roles de:
- Data Analyst
- Data Engineer
- Data Scientist (nivel junior/intermedio)

📌 Próximas mejoras (roadmap)
- Añadir validación de esquema (pydantic o pandera)
- Añadir tests unitarios (pytest)
- Añadir visualizaciones automáticas
- Dockerizar el pipeline
- Integrar un scheduler (Airflow, Prefect o cron)

👤 Autor
Juan M. de la Fuente Larrocca
Data Analyst & Data Engineer
Madrid
