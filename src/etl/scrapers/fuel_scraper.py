import pandas as pd
from io import StringIO
import requests
from bs4 import BeautifulSoup
import logging
from pydantic import BaseModel, Field, field_validator, ValidationError
from pathlib import Path
from src.database import get_engine

URL = "https://gasprices.aaa.com/state-gas-price-averages/"
LOG_PATH = Path(__file__).resolve().parents[3] / "logs" / "fuel_scraper.log"
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
    en el import time.
    """
    engine = get_engine()
    logger.info("Iniciando scraping de precios AAA")
    try:
        response = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        if not table:
            raise ValueError("No se encontró la tabla en la URL")

        df = pd.read_html(str(table))[0]

        # Normalizar columnas esperadas (algunas versiones de la web pueden variar)
        expected_cols = ['state', 'regular', 'mid_grade', 'premium', 'diesel']
        if df.shape[1] >= 5:
            df = df.iloc[:, :5]
            df.columns = expected_cols
        else:
            raise ValueError("La tabla no tiene las columnas esperadas")

        valid_rows = []
        for _, row in df.iterrows():
            try:
                data = row.to_dict()
                # Normalizar valores monetarios a float
                for col in ['regular', 'mid_grade', 'premium', 'diesel']:
                    val = data.get(col)
                    if pd.isna(val):
                        data[col] = None
                    elif isinstance(val, str):
                        cleaned = val.replace('$', '').replace(',', '').strip()
                        data[col] = float(cleaned) if cleaned not in ("", "—", "-") else None
                    else:
                        data[col] = float(val) if val is not None else None

                # Validación con pydantic (omitimos filas con valores faltantes en campos obligatorios)
                validated = FuelPriceSchema(**data)
                valid_rows.append(validated.model_dump())
            except ValidationError as e:
                logger.warning(f"Fila omitida: {data.get('state')} - {e}")
            except Exception as e:
                logger.debug(f"Ignorando fila por error de parseo: {e}")

        if not valid_rows:
            logger.warning("No se obtuvieron filas válidas del scraping")
            return

        df_clean = pd.DataFrame(valid_rows)

        # Guardar en la base de datos
        df_clean.to_sql('fuel_prices', engine, if_exists='replace', index=False)
        logger.info(f"Completado: {len(df_clean)} estados guardados en 'fuel_prices'")

    except requests.RequestException as re:
        logger.exception(f"Error de red al obtener la página: {re}")
    except Exception as e:
        logger.exception(f"Error en scrape_fuel_prices: {e}")

if __name__ == "__main__":
    scrape_fuel_prices()
