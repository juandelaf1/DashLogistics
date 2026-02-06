# src/etl/etl.py
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

import pandas as pd
from pydantic import BaseModel, Field, field_validator, ValidationError

from src.database import get_engine

load_dotenv()

# Rutas configurables mediante .env
RAW_PATH = Path(os.getenv("RAW_DATA_PATH", "data/raw/shipping_data.csv"))
CLEAN_PATH = Path(os.getenv("CLEAN_DATA_PATH", "data/clean/shipping_data_clean.csv"))
BASE_DIR = Path(__file__).resolve().parents[3]
LOG_PATH = BASE_DIR / "logs" / "etl.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# Logging básico
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Esquema de validación
class ShippingDataSchema(BaseModel):
    rank: int = Field(ge=1)
    state: str
    postal: str = Field(min_length=2, max_length=2)
    population: float = Field(gt=0)

    @field_validator("state")
    @classmethod
    def state_to_upper(cls, v):
        return v.strip().upper()

# Funciones ETL
def load_data():
    logger.info(f"Cargando datos desde {RAW_PATH}")
    if not RAW_PATH.exists():
        logger.error(f"No se encontró el archivo: {RAW_PATH}")
        raise FileNotFoundError(f"No se encontró el archivo: {RAW_PATH}")
    df = pd.read_csv(RAW_PATH)
    logger.info(f"Datos cargados correctamente. Filas: {len(df)}")
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Iniciando limpieza y validación de datos")
    # Normalizar nombres de columnas
    df = df.copy()
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    # Trim strings
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
    valid_rows = []
    invalid_count = 0
    for index, row in df.iterrows():
        try:
            validated = ShippingDataSchema(**row.to_dict())
            valid_rows.append(validated.model_dump())
        except ValidationError as e:
            invalid_count += 1
            logger.warning(f"Fila {index} descartada por validación: {e}")
    if invalid_count:
        logger.info(f"Se descartaron {invalid_count} filas no válidas")
    df_clean = pd.DataFrame(valid_rows)
    # Métricas adicionales
    if "population" in df_clean.columns and "rank" in df_clean.columns:
        df_clean["population_per_rank"] = df_clean["population"] / df_clean["rank"]
        logger.info("Columna population_per_rank creada")
    df_clean = df_clean.drop_duplicates()
    df_clean = df_clean.dropna(subset=["state"])
    if "population" in df_clean.columns:
        df_clean = df_clean.sort_values(by="population", ascending=False)
    logger.info(f"Limpieza completada. Filas finales: {len(df_clean)}")
    return df_clean

def save_data(df: pd.DataFrame):
    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    run_id = os.getenv("PIPELINE_RUN_ID")
    if run_id is not None:
        df = df.copy()
        df["pipeline_run_id"] = run_id
    df.to_csv(CLEAN_PATH, index=False)
    logger.info(f"Datos limpios guardados en CSV: {CLEAN_PATH}")

def run_etl():
    logger.info("=== INICIO DEL ETL ===")
    try:
        # 1. Extraer
        df = load_data()

        # 2. Transformar y validar
        df_clean = clean_data(df)

        # 3. Guardar CSV limpio
        save_data(df_clean)

        # 4. Cargar en la base de datos
        logger.info("Subiendo datos validados a la base de datos...")
        engine = get_engine()
        run_id = os.getenv("PIPELINE_RUN_ID")
        if run_id is not None and "pipeline_run_id" not in df_clean.columns:
            df_clean = df_clean.copy()
            df_clean["pipeline_run_id"] = run_id

        # Es seguro usar to_sql con if_exists='replace' para pipelines idempotentes
        df_clean.to_sql(name="shipping_stats", con=engine, if_exists="replace", index=False)
        logger.info("Tabla 'shipping_stats' actualizada con éxito en la base de datos")
        logger.info("=== ETL COMPLETADO ===")
    except Exception as e:
        logger.critical("Error crítico en el pipeline ETL", exc_info=True)
        raise

if __name__ == "__main__":
    run_etl()
