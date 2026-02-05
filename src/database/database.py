import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# Prioridad 1: Variable de entorno completa
DATABASE_URL = os.getenv("DATABASE_URL")

# Prioridad 2: Construcción manual para entorno local
if not DATABASE_URL:
    DB_USER = "postgres"
    DB_PASS = "admin"
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = "shipping_db"
    
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"

engine = create_engine(DATABASE_URL)

def get_engine():
    return engine

if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            print(f"✅ Conexión exitosa a la base de datos de DashLogistics")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")