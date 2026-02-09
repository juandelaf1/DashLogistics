# ruff: noqa: E402
import logging
from pathlib import Path
import os
# Importar funciones directamente para facilitar testing y control de errores
from src.utils.download_data import download_dataset
from src.etl.etl import run_etl
from src.etl.scrapers.fuel_scraper import scrape_fuel_prices
# from src.etl.scrapers.update_master_data import update_everything
from src.etl.enrichment.weather_api import get_weather_data
# Generar un run_id para trazabilidad y añadirlo como filtro de logging
import uuid

# Asegurarnos de que cada ejecución tenga un ID único (se puede pasar desde entorno)
RUN_ID = os.getenv("PIPELINE_RUN_ID") or uuid.uuid4().hex
os.environ["PIPELINE_RUN_ID"] = RUN_ID

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
    format="%(asctime)s - %(levelname)s - %(run_id)s - %(message)s",
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
        # Algunos handlers pueden no tener formatter configurado aún
        h.setFormatter(RunIdFormatter(h.formatter._fmt))
    except Exception:
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
        # Importación lazy: evita errores en pytest/IDE si el módulo no existe en tiempo de importación
        try:
            from src.etl.scrapers.update_master_data import update_everything
        except ImportError:
            logging.getLogger(__name__).warning(
                "update_master_data no disponible; se omite la actualización maestra en esta ejecución."
            )
        else:
            try:
                update_everything()
            except Exception:
                logging.exception("Fallo durante update_everything(); se continúa con el pipeline.")

        logging.info("Enriquecimiento con clima...")
        try:
            get_weather_data()
        except Exception:
            logging.exception("Fallo durante el enriquecimiento meteorológico; se continúa con el pipeline.")

        logging.info("=== PIPELINE COMPLETADO CON ÉXITO ===")
    except Exception as e:
        logging.critical(f"El pipeline se detuvo por un error: {e}")
        raise


if __name__ == "__main__":
    run_pipeline()
