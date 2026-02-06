import pandas as pd
import requests
from bs4 import BeautifulSoup
import logging
from pydantic import BaseModel, Field, field_validator, ValidationError
from pathlib import Path
from src.database import get_engine

URL = "https://gasprices.aaa.com/state-gas-price-averages/"
LOG_PATH = Path(__file__).resolve().parents[3] / "logs" / "fuel_scraper.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

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
        df.columns = ['state', 'regular', 'mid_grade', 'premium', 'diesel']

        valid_rows = []
        for _, row in df.iterrows():
            try:
                data = row.to_dict()
                for col in ['regular', 'mid_grade', 'premium', 'diesel']:
                    if isinstance(data[col], str):
                        data[col] = float(data[col].replace('$', '').strip())

                validated = FuelPriceSchema(**data)
                valid_rows.append(validated.model_dump())
            except ValidationError as e:
                logger.warning(f"Fila omitida: {data.get('state')} - {e}")

        df_clean = pd.DataFrame(valid_rows)
        df_clean.to_sql('fuel_prices', engine, if_exists='replace', index=False)
        logger.info(f"Completado: {len(df_clean)} estados en DB")

    except Exception as e:
        logger.exception(f"Error en scrape_fuel_prices: {e}")

if __name__ == "__main__":
    scrape_fuel_prices()
