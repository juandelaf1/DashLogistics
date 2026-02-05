import sys
from pathlib import Path

# --- PARCHE DE RUTAS PARA DASH LOGISTICS ---
sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
import requests
import logging
from io import StringIO
from database import get_engine

# Configuración de Pandas y Logging
pd.set_option('future.no_silent_downcasting', True)

# Ruta de log absoluta basada en la ubicación del archivo
LOG_PATH = Path(__file__).resolve().parent.parent.parent / "logs" / "master_update.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)

engine = get_engine()

def update_everything():
    logger.info("Iniciando actualización de la tabla maestra...")

    # Localizar CSV limpio usando Pathlib (raíz del proyecto)
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    csv_path = base_dir / "data" / "clean" / "shipping_data_clean.csv"

    if not csv_path.exists():
        logger.error(f"Archivo no encontrado en: {csv_path}")
        return

    try:
        df_original = pd.read_csv(csv_path)
        df_original['state'] = df_original['state'].astype(str).str.strip().str.upper()
        
        # 1. Scraping Wikipedia (Población actualizada)
        logger.info("Extrayendo población de Wikipedia...")
        url = "https://en.wikipedia.org/wiki/List_of_U.S._states_and_territories_by_population"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        tables = pd.read_html(StringIO(response.text))
        
        df_wiki = tables[0].iloc[:, [2, 3]].copy()
        df_wiki.columns = ['state', 'new_population']
        
        df_wiki['state'] = df_wiki['state'].astype(str).str.replace(r'\[.*\]', '', regex=True).str.strip().str.upper()
        df_wiki['new_population'] = pd.to_numeric(
            df_wiki['new_population'].astype(str).str.replace(',', '').str.replace(r'\[.*\]', '', regex=True), 
            errors='coerce'
        ).astype(float)

        # Merge con datos de Wikipedia
        df_final = pd.merge(df_original, df_wiki, on='state', how='left')
        df_final['population'] = df_final['new_population'].fillna(df_final['population']).infer_objects(copy=False)
        df_final = df_final.drop(columns=['new_population'])
        
        # 2. Sincronización con tabla de Diesel (PostgreSQL)
        logger.info("Sincronizando con precios de Diesel desde DB...")
        df_diesel = pd.read_sql("SELECT state, diesel FROM fuel_prices", engine)
        df_diesel['state'] = df_diesel['state'].astype(str).str.strip().str.upper()
        
        df_final = pd.merge(df_final, df_diesel, on='state', how='left')
        
        # 3. Creación de métrica de valor
        df_final['pop_per_dollar'] = df_final['population'] / df_final['diesel']

        # 4. Carga final a la tabla Master
        df_final.to_sql('master_shipping_data', engine, if_exists='replace', index=False)
        logger.info("Éxito: Tabla 'master_shipping_data' actualizada correctamente.")
        print("✅ Actualización maestra completada (Wikipedia + Diesel).")

    except Exception as e:
        logger.error(f"Error durante el proceso maestro: {e}")
        print(f"❌ Error en master_update: {e}")

if __name__ == "__main__":
    update_everything()