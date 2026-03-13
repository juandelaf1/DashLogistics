# ruff: noqa: E402
"""
DashLogistics: Data Pipeline MVP
Orquestador principal del ETL + Enriquecimiento de datos.
"""
import logging
from pathlib import Path
import os
import uuid
import pandas as pd

# Core functions
from src.utils.download_data import download_dataset
from src.etl.etl import run_etl
from src.etl.scrapers.fuel_scraper import scrape_fuel_prices
from src.etl.enrichment.weather_api import get_weather_data
from src.database import get_engine

# Setup
RUN_ID = os.getenv("PIPELINE_RUN_ID") or uuid.uuid4().hex
os.environ["PIPELINE_RUN_ID"] = RUN_ID

LOG_PATH = Path("logs/pipeline.log")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logging.getLogger().addHandler(console)
logger = logging.getLogger(__name__)


def create_enriched_dataset():
    """
    Crea el dataset final enriquecido combinando:
    - Datos de envíos (shipping_stats)
    - Precios de combustible (fuel_prices)
    - Datos climáticos (weather_data) - opcional
    
    Guarda en: data/final/enriched_data.csv
    """
    try:
        engine = get_engine()
        
        # Leer datos de todas las fuentes
        df_shipping = pd.read_sql("SELECT * FROM shipping_stats", engine)
        df_fuel = pd.read_sql("SELECT * FROM fuel_prices", engine)
        
        if df_shipping.empty:
            logger.warning("shipping_stats vacío")
            return None
        
        logger.info(f"Merging datasets: {df_shipping.shape[0]} shipping × {df_fuel.shape[0]} fuel")
        
        # Merge 1: Shipping + Fuel
        df = df_shipping.merge(
            df_fuel[['state', 'regular', 'mid_grade', 'premium', 'diesel']],
            on='state',
            how='left'
        )
        
        # Merge 2: + Weather (opcional, si existe tabla)
        try:
            df_weather = pd.read_sql("SELECT * FROM weather_data", engine)
            if not df_weather.empty:
                df = df.merge(
                    df_weather[['state', 'temperature', 'condition', 'humidity', 'wind_speed', 'feels_like']],
                    on='state',
                    how='left'
                )
                logger.info(f"✅ Weather data merged: {df_weather.shape[0]} records")
            else:
                logger.warning("Weather data table empty")
        except Exception as e:
            logger.warning(f"Weather data unavailable (optional): {e}")
        
        # Organizar columnas
        final_cols = ['rank', 'state', 'postal', 'population', 'population_per_rank',
                      'regular', 'mid_grade', 'premium', 'diesel',
                      'temperature', 'condition', 'humidity', 'wind_speed', 'feels_like',
                      'pipeline_run_id']
        
        # Solo seleccionar columnas que existen
        existing_cols = [c for c in final_cols if c in df.columns]
        df_final = df[existing_cols]
        
        # Guardar CSV
        output_dir = Path("data/final")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "enriched_data.csv"
        
        df_final.to_csv(output_path, index=False)
        logger.info(f"✅ Enriched dataset saved: {output_path} ({df_final.shape[0]} rows, {df_final.shape[1]} cols)")
        
        return df_final
    
    except Exception as e:
        logger.error(f"Error creating enriched dataset: {e}")
        return None


def run_pipeline():
    """Ejecuta el pipeline completo de ETL + Enriquecimiento."""
    logger.info("=" * 60)
    logger.info("DASHLOGISTICS ETL PIPELINE (MVP)")
    logger.info(f"Run ID: {RUN_ID}")
    logger.info("=" * 60)
    
    try:
        # 1. Descargar datos raw
        logger.info("▶ Step 1: Downloading raw data...")
        download_dataset()
        
        # 2. ETL Principal
        logger.info("▶ Step 2: Running ETL (clean & validate)...")
        run_etl()
        
        # 3. Scraping de combustible
        logger.info("▶ Step 3: Scraping fuel prices...")
        scrape_fuel_prices()
        
        # 4. Enriquecimiento con clima
        logger.info("▶ Step 4: Enriching with weather data...")
        try:
            get_weather_data()
        except Exception as e:
            logger.warning(f"Weather enrichment failed (non-critical): {e}")
        
        # 5. Crear dataset final
        logger.info("▶ Step 5: Creating final enriched dataset...")
        create_enriched_dataset()
        
        logger.info("=" * 60)
        logger.info("✅ PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
    
    except Exception as e:
        logger.critical(f"❌ PIPELINE FAILED: {e}")
        raise


if __name__ == "__main__":
    run_pipeline()
