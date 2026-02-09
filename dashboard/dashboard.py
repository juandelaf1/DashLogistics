import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="DashLogistics", layout="wide")

def get_data():
    try:
        engine = create_engine(os.getenv("DATABASE_URL"))
        df = pd.read_sql(text("SELECT * FROM shipping_stats"), engine)
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return None

def get_fuel_data():
    try:
        engine = create_engine(os.getenv("DATABASE_URL"))
        df = pd.read_sql(text("SELECT * FROM fuel_prices"), engine)
        return df
    except Exception as e:
        return None

st.title("🚢 DashLogistics Dashboard")
st.write("Shipping Data Analysis & Fuel Prices")

# Cargar datos
df = get_data()
df_fuel = get_fuel_data()

if df is not None and not df.empty:
    # KPIs principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total States", len(df))
    with col2:
        st.metric("Total Population", f"{df['population'].sum():,}")
    with col3:
        st.metric("Avg Rank", f"{df['rank'].mean():.1f}")
    with col4:
        if 'population_per_rank' in df.columns:
            st.metric("Efficiency", f"{df['population_per_rank'].mean():,.0f}")
        else:
            st.metric("Efficiency", "N/A")
    
    # Gráfico principal mejorado
    st.subheader("📊 Population vs Shipping Rank")
    fig = px.scatter(df, x="population", y="rank", hover_name="state",
                    size=df['population_per_rank'] if 'population_per_rank' in df.columns else None,
                    color="population",
                    title="Population vs Shipping Rank by State",
                    labels={"population": "Population", "rank": "Shipping Rank"})
    
    # Añadir línea de tendencia
    fig.update_layout(showlegend=True)
    st.plotly_chart(fig, width='stretch')
    
    # Tabs para diferentes análisis
    tab1, tab2, tab3 = st.tabs(["📈 Analysis", "⛽ Fuel Prices", "📊 Raw Data"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Top 10 Most Populous")
            top_pop = df.nlargest(10, 'population')[['state', 'population', 'rank']]
            st.dataframe(top_pop, width='stretch')
        
        with col2:
            st.subheader("📉 Top 10 Best Rank")
            best_rank = df.nsmallest(10, 'rank')[['state', 'population', 'rank']]
            st.dataframe(best_rank, width='stretch')
        
        # Histograma de población
        st.subheader("Population Distribution")
        fig_hist = px.histogram(df, x="population", nbins=20, 
                              title="Population Distribution Across States")
        st.plotly_chart(fig_hist, width='stretch')
    
    with tab2:
        if df_fuel is not None and not df_fuel.empty:
            st.subheader("⛽ Fuel Price Analysis")
            
            # Métricas de combustible
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Regular Avg", f"${df_fuel['regular'].mean():.2f}")
            with col2:
                st.metric("Diesel Avg", f"${df_fuel['diesel'].mean():.2f}")
            with col3:
                st.metric("Price Range", f"${(df_fuel['regular'].max() - df_fuel['regular'].min()):.2f}")
            
            # Gráfico de precios
            fuel_melted = df_fuel.melt(id_vars=['state'], 
                                     value_vars=['regular', 'mid_grade', 'premium', 'diesel'],
                                     var_name='fuel_type', value_name='price')
            
            fig_fuel = px.bar(fuel_melted.head(30), x='state', y='price', 
                            color='fuel_type', title="Fuel Prices by State (Top 30)")
            st.plotly_chart(fig_fuel, width='stretch')
        else:
            st.warning("⚠️ Fuel price data not available")
    
    with tab3:
        st.subheader("📊 Raw Shipping Data")
        st.dataframe(df, width='stretch')
        
else:
    st.error("❌ No data available")
    st.info("💡 Run `python main.py` first to process the data")
    
    # Debug info
    with st.expander("🔍 Debug Information"):
        db_url = os.getenv("DATABASE_URL", "Not set")
        st.code(f"DATABASE_URL: {db_url}")
        
        if st.button("Test Database Connection"):
            try:
                engine = create_engine(os.getenv("DATABASE_URL"))
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT COUNT(*) FROM shipping_stats")).fetchone()
                    st.success(f"Database connected. Records found: {result[0]}")
            except Exception as e:
                st.error(f"Connection failed: {e}")
