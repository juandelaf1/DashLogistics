import os
import logging
from pathlib import Path
import time

import pandas as pd
import requests
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

from src.database import get_engine, write_df_to_sql, read_sql_query
from src.utils.state_mapper import normalize_state_code, get_city_for_state

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[3]
LOG_PATH = BASE_DIR / "logs" / "weather_api.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

class WeatherDataSchema(BaseModel):
    state: str = Field(min_length=2, max_length=2)
    temperature: float = Field(description="Temperatura en Fahrenheit")
    condition: str = Field(min_length=1, description="Condición climática")
    humidity: float = Field(ge=0, le=100, description="Humedad relativa 0-100%")
    wind_speed: float = Field(ge=0, description="Velocidad del viento mph")
    feels_like: float = Field(description="Sensación térmica Fahrenheit")
    data_source: str = Field(default="OpenWeatherMap")

    @field_validator('state')
    @classmethod
    def state_must_be_code(cls, v):
        return normalize_state_code(v)


def get_weather_for_state(state_code: str) -> dict:
    if not OPENWEATHER_API_KEY:
        raise ValueError("OPENWEATHER_API_KEY no configurada en .env")

    state_code = normalize_state_code(state_code)
    city = get_city_for_state(state_code)

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': f"{city},{state_code},US",
        'appid': OPENWEATHER_API_KEY,
        'units': 'imperial',
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        main = data['main']
        wind = data['wind']
        weather = data['weather'][0]

        return {
            'state': state_code,
            'temperature': main['temp'],
            'condition': weather['description'].title(),
            'humidity': main['humidity'],
            'wind_speed': wind['speed'],
            'feels_like': main['feels_like'],
            'data_source': 'OpenWeatherMap',
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Error de red obteniendo clima para {state_code}: {e}")
        raise
    except (KeyError, ValueError) as e:
        logger.error(f"Error parsing respuesta de {state_code}: {e}")
        raise


def get_weather_data():
    logger.info("Iniciando consulta de datos meteorológicos...")

    if not OPENWEATHER_API_KEY:
        logger.error("OPENWEATHER_API_KEY no configurada en .env")
        return pd.DataFrame()

    engine = get_engine()

    try:
        df_states = read_sql_query("SELECT DISTINCT state FROM shipping_stats", engine)
    except Exception as e:
        logger.error(f"Error leyendo estados desde BD: {e}")
        return pd.DataFrame()

    if df_states.empty:
        logger.warning("No hay estados en shipping_stats")
        return pd.DataFrame()

    weather_results = []
    failed_states = []

    for state in df_states['state'].unique():
        try:
            weather_data = get_weather_for_state(state)
            weather_results.append(weather_data)
            logger.info(f"{state}: Clima obtenido")
            time.sleep(0.3)
        except Exception as e:
            logger.warning(f"{state}: {e}")
            failed_states.append(state)

    if not weather_results:
        logger.error("No se pudieron obtener datos climáticos")
        return pd.DataFrame()

    df_weather = pd.DataFrame(weather_results)

    try:
        write_df_to_sql(df_weather, 'weather_data', engine)
        logger.info(f"{len(weather_results)} registros climáticos guardados")
    except Exception as e:
        logger.error(f"Error guardando weather_data: {e}")

    if failed_states:
        logger.warning(f"{len(failed_states)} estados sin clima: {failed_states}")

    return df_weather


if __name__ == "__main__":
    get_weather_data()
