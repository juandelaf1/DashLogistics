# src/etl/enrichment/weather_api.py
import os
import logging
from pathlib import Path
import time

import pandas as pd
import requests
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from src.database import get_engine

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[3]
LOG_PATH = BASE_DIR / "logs" / "weather_api.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# API Keys - Prioridad: WeatherAPI.com (más robusto y gratuito)
WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")
OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")

class WeatherDataSchema(BaseModel):
    state: str
    temperature: float = Field(description="Temperatura en Fahrenheit")
    condition: str = Field(min_length=1, description="Condición climática")
    humidity: float = Field(ge=0, le=100, description="Humedad relativa")
    wind_speed: float = Field(ge=0, description="Velocidad del viento mph")
    feels_like: float = Field(description="Sensación térmica")
    data_source: str = Field(description="API source")

def get_weather_data_weatherapi(state_code: str) -> dict:
    if not WEATHERAPI_KEY:
        raise ValueError("WEATHERAPI_KEY no configurada")

    state_cities = {
        'CA': 'Los Angeles', 'TX': 'Houston', 'FL': 'Miami', 'NY': 'New York',
        'PA': 'Philadelphia', 'IL': 'Chicago', 'OH': 'Columbus', 'GA': 'Atlanta',
        'NC': 'Charlotte', 'MI': 'Detroit', 'NJ': 'Newark', 'VA': 'Virginia Beach',
        'WA': 'Seattle', 'AZ': 'Phoenix', 'MA': 'Boston', 'TN': 'Memphis',
        'IN': 'Indianapolis', 'MO': 'Kansas City', 'MD': 'Baltimore', 'WI': 'Milwaukee',
        'CO': 'Denver', 'MN': 'Minneapolis', 'SC': 'Columbia', 'AL': 'Birmingham',
        'LA': 'New Orleans', 'KY': 'Louisville', 'OR': 'Portland', 'OK': 'Oklahoma City',
        'CT': 'Hartford', 'UT': 'Salt Lake City', 'IA': 'Des Moines', 'NV': 'Las Vegas',
        'AR': 'Little Rock', 'MS': 'Jackson', 'KS': 'Wichita', 'NM': 'Albuquerque',
        'NE': 'Omaha', 'WV': 'Charleston', 'ID': 'Boise', 'HI': 'Honolulu',
        'NH': 'Manchester', 'ME': 'Portland', 'MT': 'Billings', 'RI': 'Providence',
        'DE': 'Wilmington', 'SD': 'Sioux Falls', 'ND': 'Fargo', 'AK': 'Anchorage',
        'VT': 'Burlington', 'WY': 'Cheyenne'
    }

    city = state_cities.get(state_code, state_code)

    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        'key': WEATHERAPI_KEY,
        'q': f"{city}, {state_code}, USA",
        'aqi': 'no'
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        current = data['current']

        return {
            'state': state_code,
            'temperature': current['temp_f'],
            'condition': current['condition']['text'],
            'humidity': current['humidity'],
            'wind_speed': current['wind_mph'],
            'feels_like': current['feelslike_f'],
            'data_source': 'WeatherAPI.com'
        }

    except Exception:
        logger.exception(f"Error obteniendo datos de WeatherAPI para {state_code}")
        raise

def get_weather_data_openweather(state_code: str) -> dict:
    if not OPENWEATHER_KEY:
        raise ValueError("OPENWEATHER_API_KEY no configurada")

    state_coords = {
        'CA': (36.7783, -119.4179), 'TX': (31.9686, -99.9018), 'FL': (27.6648, -81.5158),
        'NY': (43.0, -75.0), 'PA': (41.2033, -77.1945), 'IL': (40.6331, -89.3985),
    }

    if state_code not in state_coords:
        logger.warning(f"Coordenadas no disponibles para {state_code}")
        return None

    lat, lon = state_coords[state_code]

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': OPENWEATHER_KEY,
        'units': 'imperial'
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        main = data['main']
        weather = data['weather'][0]

        return {
            'state': state_code,
            'temperature': main['temp'],
            'condition': weather['description'].title(),
            'humidity': main['humidity'],
            'wind_speed': data.get('wind', {}).get('speed', 0),
            'feels_like': main['feels_like'],
            'data_source': 'OpenWeather'
        }

    except Exception:
        logger.exception(f"Error obteniendo datos de OpenWeather para {state_code}")
        raise

def get_weather_data():
    logger.info("Iniciando consulta de datos meteorológicos...")

    if not WEATHERAPI_KEY and not OPENWEATHER_KEY:
        logger.error("No hay API keys configuradas.")
        return

    engine = get_engine()

    try:
        df_states = pd.read_sql("SELECT DISTINCT state FROM shipping_stats", engine)
    except Exception:
        logger.exception("Error al leer estados desde shipping_stats")
        return

    if df_states.empty:
        logger.warning("No hay estados en shipping_stats para consultar clima")
        return

    weather_results = []
    failed_states = []

    for state in df_states['state']:
        try:
            if WEATHERAPI_KEY:
                try:
                    weather_data = get_weather_data_weatherapi(state)
                    weather_results.append(weather_data)
                    logger.info(f"✅ {state}: Datos obtenidos de WeatherAPI.com")
                    time.sleep(0.5)
                    continue
                except Exception as e:
                    logger.warning(f"WeatherAPI falló para {state}: {e}")

            if OPENWEATHER_KEY:
                try:
                    weather_data = get_weather_data_openweather(state)
                    if weather_data:
                        weather_results.append(weather_data)
                        logger.info(f"✅ {state}: Datos obtenidos de OpenWeather (fallback)")
                        time.sleep(0.5)
                        continue
                except Exception as e:
                    logger.warning(f"OpenWeather falló para {state}: {e}")

            logger.error(f"❌ {state}: Todas las APIs fallaron")
            failed_states.append(state)

        except Exception as e:
            logger.error(f"Error procesando {state}: {e}")
            failed_states.append(state)

    if not weather_results:
        logger.error("No se pudieron obtener datos climáticos")
        return

    try:
        df_weather = pd.DataFrame(weather_results)
        df_weather.to_sql('weather_data', engine, if_exists='replace', index=False)
        logger.info(f"✅ {len(weather_results)} registros climáticos guardados en weather_data")

        try:
            df_master = pd.read_sql("SELECT * FROM master_shipping_data", engine)
            df_master_updated = pd.merge(
                df_master,
                df_weather,
                on='state',
                how='left'
            )
            df_master_updated.to_sql('master_shipping_data', engine, if_exists='replace', index=False)
            logger.info("✅ Tabla master_shipping_data actualizada con datos climáticos")
        except Exception as e:
            logger.warning(f"No se pudo actualizar master_shipping_data: {e}")

        if failed_states:
            logger.warning(f"Estados fallidos: {failed_states}")

    except Exception:
        logger.exception("Error guardando datos climáticos en la base de datos")
        raise

if __name__ == "__main__":
    get_weather_data()
    logger.exception("Error guardando datos climáticos en la base de datos")
    raise

if __name__ == "__main__":
    get_weather_data()
