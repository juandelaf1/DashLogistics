import pandas as pd
from io import StringIO
import requests
from bs4 import BeautifulSoup
import logging
import os
from pydantic import BaseModel, Field, field_validator, ValidationError
from pathlib import Path
from src.database import get_engine

URL = "https://gasprices.aaa.com/state-gas-price-averages/"
BASE_DIR = Path(__file__).resolve().parents[3]
LOG_PATH = BASE_DIR / "logs" / "fuel_scraper.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

class FuelPriceSchema(BaseModel):
    state: str
    regular: float = Field(gt=0)
    mid_grade: float = Field(gt=0)
    premium: float = Field(gt=0)
    diesel: float = Field(gt=0)

    @field_validator('state')
    @classmethod
    def clean_state(cls, v):
        return v.strip().upper()

def scrape_fuel_prices():
    """
    Scrapea la tabla de precios de gasolina desde AAA y guarda en la tabla `fuel_prices`.
    La conexión a la base de datos se crea dentro de la función para evitar efectos secundarios
    en el import time. Incluye trazabilidad completa con run_id.
    """
    # Obtener run_id para trazabilidad
    run_id = os.getenv("PIPELINE_RUN_ID")
    if run_id:
        logger.info(f"Iniciando scraping de precios AAA con run_id: {run_id}")
    else:
        logger.warning("PIPELINE_RUN_ID no encontrado en entorno")
        run_id = "unknown"
    
    engine = get_engine()
    logger.info("Iniciando scraping de precios AAA")
    try:
        response = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        if not table:
            raise ValueError("No se encontró la tabla en la URL")

        df = pd.read_html(StringIO(str(table)))[0]

        # Normalizar columnas esperadas (algunas versiones de la web pueden variar)
        expected_cols = ['state', 'regular', 'mid_grade', 'premium', 'diesel']
        if df.shape[1] >= 5:
            df.columns = expected_cols
        else:
            logger.warning(f"Columnas inesperadas: {df.columns.tolist()}")
            # Intentar mapeo automático
            col_mapping = {}
            for i, col in enumerate(df.columns):
                if i < len(expected_cols):
                    col_mapping[col] = expected_cols[i]
            df = df.rename(columns=col_mapping)

        # Validar y limpiar datos
        valid_rows = []
        invalid_count = 0
        
        for index, row in df.iterrows():
            try:
                # Limpiar valores numéricos
                cleaned_row = {}
                cleaned_row['state'] = str(row.iloc[0]).strip().upper()
                
                for col in ['regular', 'mid_grade', 'premium', 'diesel']:
                    if col in expected_cols:
                        # Encontrar el índice correcto de la columna
                        col_idx = expected_cols.index(col)
                        if col_idx < len(row):
                            value = str(row.iloc[col_idx]).replace('$', '').replace(',', '')
                            try:
                                cleaned_row[col] = float(value)
                            except ValueError:
                                cleaned_row[col] = None
                        else:
                            cleaned_row[col] = None
                
                # Validar con Pydantic
                validated = FuelPriceSchema(**cleaned_row)
                valid_rows.append(validated.model_dump())
                
            except (ValidationError, ValueError, IndexError) as e:
                invalid_count += 1
                logger.warning(f"Fila {index} descartada: {e}")

        if invalid_count:
            logger.info(f"Se descartaron {invalid_count} filas no válidas")

        if not valid_rows:
            raise ValueError("No se encontraron datos válidos después de la validación")

        df_clean = pd.DataFrame(valid_rows)
        
        # Añadir trazabilidad
        df_clean['pipeline_run_id'] = run_id
        df_clean['scraped_at'] = pd.Timestamp.now()
        df_clean['data_source'] = 'AAA'

        # Guardar en base de datos
        df_clean.to_sql('fuel_prices', engine, if_exists='replace', index=False)
        
        logger.info(f"✅ {len(df_clean)} registros de precios de combustible guardados (run_id: {run_id})")
        print(f"[OK] Scraping completado: {len(df_clean)} estados procesados (run_id: {run_id})")
        
        return df_clean

    except requests.RequestException as e:
        logger.error(f"Error de red al acceder a {URL}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error durante scraping: {e}")
        raise

if __name__ == "__main__":
    scrape_fuel_prices()
