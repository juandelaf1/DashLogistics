import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="DashLogistics MVP", layout="wide")

# ----------------------------
# Función para obtener datos
# ----------------------------
@st.cache_data(ttl=300)
def get_data():
    try:
        engine = create_engine(os.getenv("DATABASE_URL"))
        df_shipping = pd.read_sql(text("SELECT * FROM shipping_stats"), engine)
        df_fuel = pd.read_sql(text("SELECT * FROM fuel_prices"), engine)
        return df_shipping, df_fuel
    except Exception as e:
        st.error(f"Database error: {e}")
        return None, None

# ----------------------------
# Título
# ----------------------------
st.title("🚢 DashLogistics MVP")
st.write("Interactive Logistics Dashboard - Population, Efficiency & Fuel Analysis")

# ----------------------------
# Cargar datos
# ----------------------------
df_shipping, df_fuel = get_data()

if df_shipping is not None and not df_shipping.empty:

    # ----------------------------
    # Crear métricas
    # ----------------------------
    df_shipping['population_millions'] = df_shipping['population'] / 1_000_000
    df_shipping['efficiency'] = df_shipping['population'] / df_shipping['rank']

    # Merge con fuel
    if df_fuel is not None:
        df_shipping = df_shipping.merge(df_fuel[['state', 'diesel', 'regular']], on='state', how='left')

    # ----------------------------
    # Sidebar para filtros
    # ----------------------------
    st.sidebar.header("Controls")
    view_type = st.sidebar.selectbox("View", ['Population', 'Efficiency', 'Fuel', 'Combined'])
    min_pop = st.sidebar.slider("Min Population (Millions)", 0.0, float(df_shipping['population_millions'].max()), 0.0)
    max_pop = st.sidebar.slider("Max Population (Millions)", 0.0, float(df_shipping['population_millions'].max()), float(df_shipping['population_millions'].max()))
    min_eff = st.sidebar.slider("Min Efficiency", 0.0, float(df_shipping['efficiency'].max()), 0.0)
    max_eff = st.sidebar.slider("Max Efficiency", 0.0, float(df_shipping['efficiency'].max()), float(df_shipping['efficiency'].max()))
    selected_states = st.sidebar.multiselect("Select States", df_shipping['state'].tolist(), default=df_shipping['state'].tolist())

    # Aplicar filtros
    df_filtered = df_shipping[
        (df_shipping['population_millions'] >= min_pop) &
        (df_shipping['population_millions'] <= max_pop) &
        (df_shipping['efficiency'] >= min_eff) &
        (df_shipping['efficiency'] <= max_eff) &
        (df_shipping['state'].isin(selected_states))
    ]

    # ----------------------------
    # KPIs clave
    # ----------------------------
    st.header("📊 Key Metrics")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Total States", len(df_filtered))
    with col2:
        st.metric("Total Population", f"{df_filtered['population'].sum():,}")
    with col3:
        st.metric("Avg Efficiency", f"{df_filtered['efficiency'].mean():,.0f}")
    with col4:
        st.metric("Best Rank", df_filtered['rank'].min())
    with col5:
        top_state = df_filtered.nlargest(1, 'efficiency')['state'].values[0]
        st.metric("Top Efficient State", top_state)
    with col6:
        worst_state = df_filtered.nsmallest(1, 'efficiency')['state'].values[0]
        st.metric("Lowest Efficient State", worst_state)

    # ----------------------------
    # Mapas interactivos
    # ----------------------------
    st.header("🗺️ Interactive USA Map")

    if view_type == 'Population':
        fig = px.choropleth(
            df_filtered,
            locations='state',
            locationmode="USA-states",
            color='population_millions',
            scope="usa",
            color_continuous_scale="Blues",
            title="Population by State (Millions)",
            hover_data=['population', 'rank', 'efficiency', 'diesel', 'regular']
        )
    elif view_type == 'Efficiency':
        fig = px.choropleth(
            df_filtered,
            locations='state',
            locationmode="USA-states",
            color='efficiency',
            scope="usa",
            color_continuous_scale="Viridis",
            title="Efficiency by State",
            hover_data=['population', 'rank', 'diesel', 'regular']
        )
    elif view_type == 'Fuel':
        fig = px.choropleth(
            df_filtered,
            locations='state',
            locationmode="USA-states",
            color='diesel',
            scope="usa",
            color_continuous_scale="Reds",
            title="Diesel Prices by State ($)",
            hover_data=['population', 'rank', 'efficiency', 'regular']
        )
    else:  # Combined view
        fig = px.scatter_geo(
            df_filtered,
            locations='state',
            locationmode='USA-states',
            size='population_millions',
            color='efficiency',
            scope='usa',
            hover_name='state',
            hover_data=['population', 'rank', 'diesel', 'regular'],
            color_continuous_scale='Viridis',
            size_max=40,
            title="Population & Efficiency Combined"
        )

    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------
    # Scatter: Efficiency vs Rank
    # ----------------------------
    st.header("📈 Efficiency vs Rank")
    fig_scatter = px.scatter(
        df_filtered,
        x='rank',
        y='efficiency',
        size='population_millions',
        color='diesel',
        hover_name='state',
        color_continuous_scale='Reds',
        size_max=30,
        title="Rank vs Efficiency (Size=Population, Color=Diesel Price)",
        labels={'rank':'Rank Position (1=Best)','efficiency':'Efficiency Score'}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # ----------------------------
    # Histogram of Rank
    # ----------------------------
    st.header("📊 Rank Distribution")
    fig_hist = px.histogram(
        df_filtered,
        x='rank',
        nbins=20,
        title="Distribution of State Ranks",
        labels={'rank':'Rank Position'}
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    # ----------------------------
    # Correlation Heatmap
    # ----------------------------
    st.header("📉 Correlation Heatmap")
    corr_cols = ['population', 'rank', 'efficiency']
    if 'diesel' in df_filtered.columns:
        corr_cols.append('diesel')
    if 'regular' in df_filtered.columns:
        corr_cols.append('regular')
    corr = df_filtered[corr_cols].corr()

    fig_heatmap = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        colorscale='Viridis',
        zmin=-1,
        zmax=1,
        hoverongaps=False
    ))
    fig_heatmap.update_layout(title="Correlation Matrix", height=500)
    st.plotly_chart(fig_heatmap, use_container_width=True)

else:
    st.error("❌ No data available")
    st.info("💡 Run `python main.py` first to populate the database")
