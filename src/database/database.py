import os
import logging
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def _build_engine(url: str):
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(url, connect_args=connect_args)

_engine = None

def get_engine():
    global _engine
    if _engine is not None:
        return _engine

    db_url = os.getenv("DATABASE_URL")

    if db_url:
        _engine = _build_engine(db_url)
        try:
            with _engine.connect():
                logger.info(f"[OK] Conectado a: {db_url.split('://')[0]}://...")
            return _engine
        except Exception as e:
            logger.warning(f"No se pudo conectar a {db_url}: {e}")
            _engine = None

    fallback_url = os.getenv("DATABASE_FALLBACK_URL", "sqlite:///./data/dashlogistics.db")
    logger.info(f"Usando fallback SQLite: {fallback_url}")
    _engine = _build_engine(fallback_url)
    _ensure_tables(_engine)
    return _engine

def get_raw_connection(engine=None):
    if engine is None:
        engine = get_engine()
    return engine.raw_connection()

def write_df_to_sql(df, name, engine=None, if_exists="replace"):
    eng = engine or get_engine()
    with eng.connect() as conn:
        raw = conn.connection
        df.to_sql(name, raw, if_exists=if_exists, index=False)

def read_sql_query(query, engine=None):
    eng = engine or get_engine()
    import pandas as pd
    with eng.connect() as conn:
        raw = conn.connection
        return pd.read_sql_query(query, raw)

def _ensure_tables(engine):
    try:
        import pandas as pd
        inspector = __import__("sqlalchemy").inspect(engine)
        existing = inspector.get_table_names()
        for table in ["shipping_stats", "fuel_prices", "weather_data"]:
            if table not in existing:
                write_df_to_sql(pd.DataFrame(), table, engine)
                logger.info(f"Tabla '{table}' creada")
    except Exception as e:
        logger.warning(f"No se pudieron verificar tablas: {e}")

if __name__ == "__main__":
    try:
        eng = get_engine()
        with eng.connect() as conn:
            print("[OK] Conexión exitosa a la base de datos de DashLogistics")
    except Exception as e:
        print(f"[ERROR] Error de conexión: {e}")