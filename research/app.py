import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# Conexión 
DB_HOST = os.getenv("DB_HOST", "localhost")
engine = create_engine(f"postgresql://postgres:admin@{DB_HOST}:5432/shipping_db")

st.set_page_config(page_title="Shipping Data Lab", layout="wide")

st.title("📊 Shipping Analysis Dashboard")
st.markdown("Análisis de eficiencia logística y demografía de estados.")

# 1. Carga de datos
df = pd.read_sql("SELECT state, rank, population FROM shipping_stats", engine)

# 2. Sidebar para filtros
st.sidebar.header("Filtros")
min_pop = st.sidebar.slider("Población mínima", int(df.population.min()), int(df.population.max()), 0)
df_filtered = df[df.population >= min_pop]

# 3. Métricas clave
col1, col2, col3 = st.columns(3)
col1.metric("Total Estados", len(df_filtered))
col2.metric("Media Rank", round(df_filtered['rank'].mean(), 2))
col3.metric("Población Total", f"{df_filtered.population.sum():,}")

# 4. Gráfico Interactivo (Plotly)
st.subheader("Población vs Ranking")
fig = px.scatter(df_filtered, x="population", y="rank", 
                 hover_name="state", 
                 trendline="ols", # Esto muestra la regresión que hicimos en el model_1
                 title="Relación Interactiva Población/Rank",
                 color_continuous_scale="Viridis")
st.plotly_chart(fig, use_container_width=True)

# 5. Comparativa de Extremos
st.subheader("Comparativa de Extremos (Top 10 vs Bottom 10)")
df_sorted = df.sort_values('population')
extremos = pd.concat([df_sorted.head(10), df_sorted.tail(10)])
extremos['Grupo'] = ['Pequeños']*10 + ['Grandes']*10

fig2 = px.bar(extremos.groupby('Grupo')['rank'].mean().reset_index(), 
              x='Grupo', y='rank', color='Grupo',
              title="Rank Promedio por Tamaño")
st.plotly_chart(fig2)

st.write("Datos actuales en la BD:", df_filtered)