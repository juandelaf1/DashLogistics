import logging
from pathlib import Path
import sys
import os

# Asegurarnos de que `src/` esté en sys.path para imports internos
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Importar funciones directamente para facilitar testing y control de errores
from utils.download_data import download_dataset
from etl.etl import run_etl
from etl.scrapers.fuel_scraper import scrape_fuel_prices
from etl.scrapers.update_master_data import update_everything
from etl.enrichment.weather_api import get_weather_data

# Configurar logging del orquestador
# Al estar en la raíz, creará la carpeta /logs aquí mismo
LOG_PATH = Path("logs/pipeline.log")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Handler para ver la ejecución en tiempo real por terminal
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)


def run_pipeline():
    logging.info("=== INICIO DEL PIPELINE GLOBAL DASHLOGISTICS ===")
    try:
        logging.info("Ejecutando descarga de datos...")
        download_dataset()

        logging.info("Ejecutando ETL principal...")
        run_etl()

        logging.info("Scraping de precios de combustible...")
        scrape_fuel_prices()

        logging.info("Actualización maestra...")
        update_everything()

        logging.info("Enriquecimiento con clima...")
        get_weather_data()

        logging.info("=== PIPELINE COMPLETADO CON ÉXITO ===")
    except Exception as e:
        logging.critical(f"El pipeline se detuvo por un error: {e}")
        raise


if __name__ == "__main__":
    run_pipeline()