# ruff: noqa: E402
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

# Generar un run_id para trazabilidad y añadirlo como filtro de logging
import uuid

# Asegurarnos de que cada ejecución tenga un ID único (se puede pasar desde entorno)
RUN_ID = os.getenv('PIPELINE_RUN_ID') or uuid.uuid4().hex
os.environ['PIPELINE_RUN_ID'] = RUN_ID

# Configurar logging del orquestador
# Al estar en la raíz, creará la carpeta /logs aquí mismo
LOG_PATH = Path("logs/pipeline.log")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

class RunIdFilter(logging.Filter):
    def __init__(self, run_id):
        super().__init__()
        self.run_id = run_id

    def filter(self, record):
        record.run_id = self.run_id
        return True

class RunIdFormatter(logging.Formatter):
    """Formatter que garantiza que `run_id` siempre exista en el record."""
    def format(self, record):
        if not hasattr(record, "run_id"):
            record.run_id = os.getenv("PIPELINE_RUN_ID", "-")
        return super().format(record)

# Configurar logging con un formatter que no falle si `run_id` no está presente
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(run_id)s - %(message)s"
)

# Handler para ver la ejecución en tiempo real por terminal
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = RunIdFormatter("%(asctime)s - %(levelname)s - %(run_id)s - %(message)s")
console.setFormatter(formatter)
root_logger = logging.getLogger()
# Añadimos el filtro al logger raíz y aseguramos que cada handler use el RunIdFormatter
root_logger.addFilter(RunIdFilter(RUN_ID))
for h in list(root_logger.handlers):
    try:
        h.setFormatter(RunIdFormatter(h.formatter._fmt))
    except Exception:
        # Si el handler no tiene un _fmt (contrario a lo esperado), configurar un formatter por defecto
        h.setFormatter(RunIdFormatter("%(asctime)s - %(levelname)s - %(run_id)s - %(message)s"))
root_logger.addHandler(console)


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