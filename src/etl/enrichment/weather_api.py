# src/etl/enrichment/weather_api.py
"""
Módulo para enriquecimiento de datos con información climática.
Obtiene datos de WeatherAPI.com y los almacena en la base de datos.
"""
import os
import logging
from pathlib import Path
import time

import pandas as pd
import requests
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

from src.database import get_engine
from src.utils.state_mapper import normalize_state_code, get_city_for_state

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[3]
LOG_PATH = BASE_DIR / "logs" / "weather_api.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# API Key
WEATHERAPI_KEY = os.getenv("OPENWEATHER_API_KEY")

class WeatherDataSchema(BaseModel):
    """Schema de validación para datos climáticos."""
    state: str = Field(min_length=2, max_length=2)
    temperature: float = Field(description="Temperatura en Fahrenheit")
    condition: str = Field(min_length=1, description="Condición climática")
    humidity: float = Field(ge=0, le=100, description="Humedad relativa 0-100%")
    wind_speed: float = Field(ge=0, description="Velocidad del viento mph")
    feels_like: float = Field(description="Sensación térmica Fahrenheit")
    data_source: str = Field(default="WeatherAPI.com")

    @field_validator('state')
    @classmethod
    def state_must_be_code(cls, v):
        """Asegura que el estado sea código de 2 letras."""
        return normalize_state_code(v)


def get_weather_for_state(state_code: str) -> dict:
    """
    Obtiene datos climáticos para un estado usando WeatherAPI.com.
    
    Args:
        state_code: Código de estado de 2 letras (CA, NY, etc.)
        
    Returns:
        dict con temperature, condition, humidity, wind_speed, feels_like
        
    Raises:
        ValueError, requests.RequestException
    """
    if not WEATHERAPI_KEY:
        raise ValueError("WEATHERAPI_KEY no configurada en .env")
    
    # Normalizar código de estado
    state_code = normalize_state_code(state_code)
    city = get_city_for_state(state_code)
    
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
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de red obteniendo clima para {state_code}: {e}")
        raise
    except (KeyError, ValueError) as e:
        logger.error(f"Error parsing respuesta de {state_code}: {e}")
        raise

def get_weather_data():
    """Obtiene y guarda datos climáticos para todos los estados en la BD."""
    logger.info("Iniciando consulta de datos meteorológicos...")
    
    if not WEATHERAPI_KEY:
        logger.error("WEATHERAPI_KEY no configurada en .env")
        return pd.DataFrame()
    
    engine = get_engine()
    
    try:
        df_states = pd.read_sql("SELECT DISTINCT state FROM shipping_stats", engine)
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
            logger.info(f"✅ {state}: Clima obtenido")
            time.sleep(0.3)  # Rate limiting
        except Exception as e:
            logger.warning(f"❌ {state}: {e}")
            failed_states.append(state)
    
    if not weather_results:
        logger.error("No se pudieron obtener datos climáticos")
        return pd.DataFrame()
    
    df_weather = pd.DataFrame(weather_results)
    
    # Guardar a BD
    try:
        df_weather.to_sql('weather_data', engine, if_exists='replace', index=False)
        logger.info(f"✅ {len(weather_results)} registros climáticos guardados")
    except Exception as e:
        logger.error(f"Error guardando weather_data: {e}")
    
    if failed_states:
        logger.warning(f"❌ {len(failed_states)} estados sin clima: {failed_states}")
    
    return df_weather


if __name__ == "__main__":
    get_weather_data()
