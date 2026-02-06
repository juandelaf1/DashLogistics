from fastapi import FastAPI
import sqlalchemy
import os

DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI(title="DashLogistics API")

@app.get("/")
def root():
    return {"message": "API de DashLogistics funcionando"}

@app.get("/health")
def health():
    return {"status": "ok"}

# Ejemplo: devolver datos de una tabla
@app.get("/data")
def get_data():
    engine = sqlalchemy.create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute("SELECT * FROM master_table LIMIT 50")
        rows = [dict(r) for r in result]
    return rows
