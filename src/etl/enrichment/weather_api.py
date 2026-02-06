import os
import sys
import pandas as pd
import requests
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv

# Subimos dos niveles desde src/enrichment para encontrar database.py en src

from src.database import get_engine

# Cargar variables de entorno
load_dotenv()

# --- CONFIGURACIÓN ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_PATH = BASE_DIR / "logs" / "weather_api.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = get_engine()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

logger = logging.getLogger(__name__)

# --- ESQUEMA DE VALIDACIÓN ---
class WeatherDataSchema(BaseModel):
    st_ref: str
    current_temp: float
    weather_condition: str = Field(min_length=1)

# --- LÓGICA DE NEGOCIO ---
def get_weather_data():
    if not API_KEY:
        error_msg = "No se encontró OPENWEATHER_API_KEY en el entorno"
        logger.error(error_msg)
        print(f"[ERROR] {error_msg}")
        return

    logger.info("Iniciando consulta a OpenWeather API...")
    
    try:
        # Extraemos los estados de la tabla maestra
        df_states = pd.read_sql("SELECT state FROM master_shipping_data", engine)
    except Exception as e:
        logger.error(f"Error al leer master_shipping_data: {e}")
        print(f"[ERROR] Error al conectar con la DB: {e}")
        return

    weather_results = []

    for state in df_states['state']:
        # Llamada a la API (USA para asegurar precisión)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={state},USA&appid={API_KEY}&units=metric"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Preparamos datos para validar
                raw_entry = {
                    'st_ref': state,
                    'current_temp': data['main']['temp'],
                    'weather_condition': data['weather'][0]['main']
                }
                
                # Validación Pydantic
                validated = WeatherDataSchema(**raw_entry)
                weather_results.append(validated.model_dump())
                logger.info(f"Datos obtenidos para {state}: {validated.current_temp}°C")
                
            else:
                logging.warning(f"No se pudo obtener clima para {state}. Status: {response.status_code}")
        except ValidationError as ve:
            logging.error(f"Error de validación en {state}: {ve}")
        except Exception as e:
            logging.error(f"Error de conexión en {state}: {e}")

    if not weather_results:
        logger.warning("No se obtuvieron resultados válidos del clima")
        return

    # Procesamiento y Merge
    df_weather = pd.DataFrame(weather_results)
    df_master = pd.read_sql("SELECT * FROM master_shipping_data", engine)
    
    # Estandarización para cruce
    df_master['state_up'] = df_master['state'].str.strip().str.upper()
    df_weather['state_up'] = df_weather['st_ref'].str.strip().str.upper()

    # Limpieza de columnas previas si existen (Evitar duplicidad en merge)
    cols_to_drop = [c for c in ['current_temp', 'weather_condition'] if c in df_master.columns]
    if cols_to_drop:
        df_master = df_master.drop(columns=cols_to_drop)

    # Merge final
    df_final = pd.merge(df_master, df_weather.drop(columns=['st_ref']), on='state_up', how='left')
    df_final = df_final.drop(columns=['state_up'])

    # Actualización en Base de Datos
    try:
        df_final.to_sql('master_shipping_data', engine, if_exists='replace', index=False)
        logger.info("Clima integrado con éxito en 'master_shipping_data'")
        print("[OK] Clima integrado correctamente en la tabla maestra.")
    except Exception as e:
        logger.error(f"Error al guardar tabla maestra: {e}")
        print(f"[ERROR] Error al guardar en DB: {e}")

if __name__ == "__main__":
    get_weather_data()