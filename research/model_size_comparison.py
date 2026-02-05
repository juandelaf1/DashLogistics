import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import os

# Conexión
DB_HOST = os.getenv("DB_HOST", "localhost")
engine = create_engine(f"postgresql://postgres:admin@{DB_HOST}:5432/shipping_db")

def run_comparison():
    # Carga de datos
    df = pd.read_sql("SELECT state, rank, population FROM shipping_stats", engine)
    
    # Ordenar por población
    df_sorted = df.sort_values('population')
    
    # Segmentación de extremos (Top 10 inferiores y superiores)
    small_states = df_sorted.head(10)
    big_states = df_sorted.tail(10)
    
    # Cálculo de medias
    avg_rank_small = small_states['rank'].mean()
    avg_rank_big = big_states['rank'].mean()
    
    # Print directo y objetivo
    print("--- Análisis de Extremos Poblacionales ---")
    print(f"Media de Rank en estados con menor población: {avg_rank_small:.2f}")
    print(f"Media de Rank en estados con mayor población: {avg_rank_big:.2f}")
    print("------------------------------------------")
    
    # Breve nota sobre la tendencia observada
    diff = avg_rank_big - avg_rank_small
    if diff < 0:
        print(f"Tendencia: Los estados grandes ocupan puestos más altos (aprox. {abs(diff):.1f} posiciones mejor).")
    else:
        print(f"Tendencia: Los estados pequeños ocupan puestos más altos (aprox. {abs(diff):.1f} posiciones mejor).")

    # Visualización
    plt.figure(figsize=(8, 5))
    plt.bar(['10 Menos Poblados', '10 Más Poblados'], [avg_rank_small, avg_rank_big], color=['#7fb3d5', '#1a5276'])
    plt.title('Comparativa de Rank Promedio por Volumen de Población')
    plt.ylabel('Posición en el Ranking (Menor es mejor)')
    
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    plt.savefig('logs/comparativa_size.png')
    print("\nGráfica actualizada en logs/comparativa_size.png")

if __name__ == "__main__":
    run_comparison()