import pandas as pd
from sqlalchemy import create_engine

DB_HOST = os.getenv("DB_HOST", "localhost")
engine = create_engine(f"postgresql://postgres:admin@{DB_HOST}:5432/shipping_db")

def run_enrichment_pipeline():
    print("🔄 Iniciando Pipeline de Enriquecimiento...")
    
    # 1. Extracción
    df_shipping = pd.read_sql("SELECT * FROM shipping_stats", engine)
    df_fuel = pd.read_sql("SELECT * FROM fuel_prices", engine)
    
    # 2. Transformación (Limpieza y Unión)
    df_shipping['state'] = df_shipping['state'].str.strip().str.upper()
    df_fuel['state'] = df_fuel['state'].str.strip().str.upper()
    
    df_final = pd.merge(df_shipping, df_fuel, on='state', how='inner')
    
    # 3. Creación de Inteligencia (KPIs nuevos)
    # Población por cada dólar de diesel (Potencial de alcance económico)
    df_final['pop_per_dollar'] = (df_final['population'] / df_final['diesel_price']).round(2)
    
    # 4. Carga (Guardamos la tabla maestra)
    df_final.to_sql('master_shipping_data', engine, if_exists='replace', index=False)
    
    print(f"✅ Pipeline finalizado: {len(df_final)} estados procesados.")
    print("🚀 Tabla 'master_shipping_data' lista para el Dashboard.")

if __name__ == "__main__":
    run_enrichment_pipeline()