import os
import subprocess
import sys
import logging
from pathlib import Path

# Configuración de Logging
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_PATH = BASE_DIR / "logs" / "pipeline.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

def run_script(script_name):
    # Esto asegura que busque dentro de src/ incluso si se llama desde la raíz
    base_path = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_path, script_name)
    
    if not os.path.exists(script_path):
        logging.error(f"ARCHIVO NO ENCONTRADO: {script_path}")
        sys.exit(1)

    logging.info(f"EJECUTANDO: {script_name}")
    result = subprocess.run([sys.executable, script_path])
    
    if result.returncode == 0:
        logging.info(f"OK: {script_name} finalizado")
    else:
        logging.error(f"ERROR: {script_name} falló. Deteniendo pipeline.")
        sys.exit(1)

if __name__ == "__main__":
    logging.info("--- INICIO DEL PROCESO GLOBAL DASHLOGISTICS ---")
    
    # ORDEN DE TRAZABILIDAD SEGURO:
    # 1. Scraper de Diesel (Datos de coste)
    run_script("scrapers/fuel_scraper.py")
    
    # 2. Consolidación (Crea la Master Table uniendo población y diesel)
    run_script("scrapers/update_master_data.py")
    
    # 3. Enriquecimiento (Añade clima a la Master Table ya creada)
    run_script("enrichment/weather_api.py")
    
    logging.info("--- PIPELINE FINALIZADO CORRECTAMENTE ---")