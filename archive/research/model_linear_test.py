import pandas as pd
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import os

# Config de conexión
DB_HOST = os.getenv("DB_HOST", "localhost")
engine = create_engine(f"postgresql://postgres:admin@{DB_HOST}:5432/shipping_db")

def run_analysis():
    # Cargo los datos de la tabla que creamos
    df = pd.read_sql("SELECT rank, population FROM shipping_stats", engine)
    
    # Preparo variables
    X = df[['population']]
    y = df['rank']
    
    # Lanzo la regresión
    model = LinearRegression()
    model.fit(X, y)
    
    # Saco métricas para ver qué ha pasado
    r2 = r2_score(y, model.predict(X))
    mse = mean_squared_error(y, model.predict(X))
    
    print("--- Resultados Regresión ---")
    print(f"R2 score: {r2}")
    print(f"MSE: {mse}")
    
    # Mi conclusión: 
    # El R2 es bajísimo (casi 0), lo que confirma que la población no explica el rank. 
    # Como comentamos, en estados con menos gente es más fácil tener mejores ratios 
    # y por eso la regresión lineal aquí no tiene mucho sentido.
    
    # Guardo el gráfico para el readme
    plt.figure(figsize=(10, 6))
    plt.scatter(X, y, alpha=0.6)
    plt.plot(X, model.predict(X), color='red')
    plt.title('Población vs Rank')
    plt.xlabel('Población')
    plt.ylabel('Rank')
    
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    plt.savefig('logs/grafica_ml.png')
    print("Gráfica guardada en logs/grafica_ml.png")

if __name__ == "__main__":
    run_analysis()