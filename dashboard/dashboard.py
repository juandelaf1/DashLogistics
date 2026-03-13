import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parents[1]))

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

@st.cache_data(ttl=300)
def get_analysis_data():
    """Load enriched analysis data with efficiency scores."""
    try:
        analysis_path = Path("data/final/logistics_analysis_enriched.csv")
        if analysis_path.exists():
            return pd.read_csv(analysis_path)
    except Exception as e:
        st.warning(f"Could not load analysis data: {e}")
    return None

@st.cache_data(ttl=300)
def get_kpi_data():
    """Load data with advanced logistics KPIs calculated."""
    try:
        from src.analysis.kpis import (
            calculate_fuel_cost_index,
            calculate_logistics_demand_score,
            calculate_freight_opportunity_score,
            calculate_cost_efficiency_index
        )
        
        # Load enriched base data
        enriched_path = Path("data/final/enriched_data.csv")
        if enriched_path.exists():
            df = pd.read_csv(enriched_path)
            
            # Calculate KPIs
            df['fuel_cost_index'] = calculate_fuel_cost_index(df)
            df['logistics_demand_score'] = calculate_logistics_demand_score(df)
            df['freight_opportunity_score'] = calculate_freight_opportunity_score(df)
            df['cost_efficiency_index'] = calculate_cost_efficiency_index(df)
            
            # Add region information
            REGIONS = {
                'Northeast': ['CT', 'ME', 'MA', 'NH', 'RI', 'VT', 'NJ', 'NY', 'PA'],
                'South': ['DE', 'FL', 'GA', 'MD', 'NC', 'SC', 'VA', 'WV', 'AL', 'KY', 'MS', 'TN', 'AR', 'LA', 'OK', 'TX'],
                'Midwest': ['IL', 'IN', 'MI', 'OH', 'WI', 'IA', 'KS', 'MN', 'MO', 'NE', 'ND', 'SD'],
                'West': ['AZ', 'CO', 'ID', 'MT', 'NV', 'NM', 'UT', 'WY', 'AK', 'CA', 'HI', 'OR', 'WA']
            }
            
            def assign_region(state):
                for region, states in REGIONS.items():
                    if state in states:
                        return region
                return 'Other'
            
            df['region'] = df['state'].apply(assign_region)
            return df
    except Exception as e:
        st.warning(f"Could not load KPI data: {e}")
    return None

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
    # Analysis Data Section (if available)
    # ----------------------------
    df_analysis = get_analysis_data()
    
    if df_analysis is not None:
        st.header("📈 Advanced Analytics")
        
        # Create analysis tabs
        tab1, tab2, tab3 = st.tabs(["Efficiency Tiers", "Regional Analysis", "Detailed Metrics"])
        
        with tab1:
            st.subheader("State Efficiency Classification")
            
            # Efficiency tier distribution
            col1, col2 = st.columns(2)
            
            with col1:
                tier_counts = df_analysis['efficiency_tier'].value_counts()
                fig_tiers = px.pie(
                    values=tier_counts.values,
                    names=tier_counts.index,
                    title="States by Efficiency Tier",
                    color_discrete_map={
                        'Top Tier (Highly Efficient)': '#2ECC71',
                        'Mid Tier (Average)': '#F1C40F',
                        'Low Tier (Below Average)': '#E67E22',
                        'Bottom Tier (Least Efficient)': '#E74C3C'
                    }
                )
                st.plotly_chart(fig_tiers, use_container_width=True)
            
            with col2:
                st.markdown("### What do tiers mean?")
                st.markdown("""
                - **Top Tier (Green)**: Highly efficient for logistics - low fuel costs per capita
                - **Mid Tier (Yellow)**: Average efficiency - balanced operations
                - **Low Tier (Orange)**: Below average - operational challenges
                - **Bottom Tier (Red)**: Least efficient - highest fuel burdens
                """)
            
            # Show tier details
            st.markdown("### Tier Breakdown")
            for tier in ['Top Tier (Highly Efficient)', 'Mid Tier (Average)', 'Low Tier (Below Average)', 'Bottom Tier (Least Efficient)']:
                tier_df = df_analysis[df_analysis['efficiency_tier'] == tier]
                st.write(f"**{tier}**: {len(tier_df)} states")
                st.write(tier_df[['state', 'efficiency_score', 'efficiency_percentile', 'diesel']].to_string())
        
        with tab2:
            st.subheader("Regional Comparison")
            
            # Regional statistics
            regional_stats = df_analysis.groupby('region').agg({
                'diesel': 'mean',
                'regular': 'mean',
                'efficiency_score': 'mean',
                'state': 'count'
            }).rename(columns={'state': 'count'})
            
            st.dataframe(regional_stats, use_container_width=True)
            
            # Regional visualization
            fig_regional = px.bar(
                df_analysis.groupby('region')['efficiency_score'].mean().reset_index(),
                x='region',
                y='efficiency_score',
                title="Average Efficiency Score by Region",
                color='efficiency_score',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_regional, use_container_width=True)
        
        with tab3:
            st.subheader("Detailed Metrics")
            
            # Display top and bottom states
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Top 10 Most Efficient States")
                top_10 = df_analysis.nlargest(10, 'efficiency_score')[['state', 'efficiency_score', 'population', 'diesel']]
                st.dataframe(top_10, use_container_width=True)
            
            with col2:
                st.markdown("### Top 10 Least Efficient States")
                bottom_10 = df_analysis.nsmallest(10, 'efficiency_score')[['state', 'efficiency_score', 'population', 'diesel']]
                st.dataframe(bottom_10, use_container_width=True)
            
            # Correlation plot
            st.markdown("### Key Correlations")
            corr_data = df_analysis[['population', 'regular', 'diesel', 'efficiency_score']].corr()
            fig_corr = px.imshow(corr_data, text_auto=True, title="Variable Correlations")
            st.plotly_chart(fig_corr, use_container_width=True)
    
    # ----------------------------
    # Advanced Logistics KPIs Section
    # ----------------------------
    df_kpis = get_kpi_data()
    
    if df_kpis is not None and not df_kpis.empty:
        st.header("🚀 Advanced Logistics KPIs")
        
        # Create KPI tabs
        kpi_tab1, kpi_tab2, kpi_tab3, kpi_tab4 = st.tabs([
            "Freight Opportunity", 
            "Top 10 States", 
            "Demand vs Cost", 
            "Regional Efficiency"
        ])
        
        with kpi_tab1:
            st.subheader("Freight Opportunity Score - USA Choropleth Map")
            st.markdown("Composite metric showing logistics expansion potential (higher = better opportunity)")
            
            # Prepare data for choropleth
            fig_choropleth = px.choropleth(
                df_kpis,
                locations='state',
                locationmode='USA-states',
                color='freight_opportunity_score',
                scope='usa',
                color_continuous_scale='RdYlGn',
                title='Freight Opportunity Score by State (0-100)',
                hover_data={
                    'state': True,
                    'freight_opportunity_score': ':.1f',
                    'population': ':,.0f',
                    'diesel': ':.3f',
                    'region': True
                }
            )
            fig_choropleth.update_geos(showstate=True, resolution=50)
            st.plotly_chart(fig_choropleth, use_container_width=True)
            
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Highest Score", f"{df_kpis['freight_opportunity_score'].max():.1f}", 
                         df_kpis[df_kpis['freight_opportunity_score'] == df_kpis['freight_opportunity_score'].max()]['state'].values[0])
            with col2:
                st.metric("Lowest Score", f"{df_kpis['freight_opportunity_score'].min():.1f}",
                         df_kpis[df_kpis['freight_opportunity_score'] == df_kpis['freight_opportunity_score'].min()]['state'].values[0])
            with col3:
                st.metric("Average Score", f"{df_kpis['freight_opportunity_score'].mean():.1f}")
            with col4:
                st.metric("Std Deviation", f"{df_kpis['freight_opportunity_score'].std():.1f}")
        
        with kpi_tab2:
            st.subheader("Top 10 Logistics States - Freight Opportunity Score")
            
            top_10_states = df_kpis.nlargest(10, 'freight_opportunity_score')[
                ['state', 'freight_opportunity_score', 'population', 'diesel', 'region']
            ].reset_index(drop=True)
            
            fig_top10 = px.bar(
                top_10_states,
                x='freight_opportunity_score',
                y='state',
                orientation='h',
                color='freight_opportunity_score',
                color_continuous_scale='RdYlGn',
                title='Top 10 States by Freight Opportunity Score',
                hover_data={
                    'population': ':,.0f',
                    'diesel': ':.3f',
                    'region': True
                },
                labels={'freight_opportunity_score': 'Score (0-100)', 'state': 'State'}
            )
            fig_top10.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig_top10, use_container_width=True)
            
            # Display table
            st.dataframe(top_10_states, use_container_width=True, hide_index=True)
        
        with kpi_tab3:
            st.subheader("Diesel Price vs Logistics Demand Score - Regional Comparison")
            st.markdown("Shows market demand against fuel costs by region")
            
            fig_scatter_demand = px.scatter(
                df_kpis,
                x='diesel',
                y='logistics_demand_score',
                size='freight_opportunity_score',
                color='region',
                hover_name='state',
                title='Diesel Price vs Logistics Demand Score (Size=Opportunity)',
                labels={
                    'diesel': 'Diesel Price (USD/gal)',
                    'logistics_demand_score': 'Logistics Demand Score'
                },
                color_discrete_map={
                    'Northeast': '#1f77b4',
                    'South': '#ff7f0e',
                    'Midwest': '#2ca02c',
                    'West': '#d62728'
                }
            )
            fig_scatter_demand.update_traces(marker=dict(size=10, opacity=0.7))
            st.plotly_chart(fig_scatter_demand, use_container_width=True)
            
            # Correlation analysis
            corr_value = df_kpis['diesel'].corr(df_kpis['logistics_demand_score'])
            st.info(f"📊 Correlation between Diesel Price and Logistics Demand: **{corr_value:.3f}**")
        
        with kpi_tab4:
            st.subheader("Cost Efficiency Index by Region")
            st.markdown("Compares logistics demand relative to fuel costs by region")
            
            # Calculate regional cost efficiency
            regional_efficiency = df_kpis.groupby('region').agg({
                'cost_efficiency_index': 'mean',
                'fuel_cost_index': 'mean',
                'logistics_demand_score': 'mean',
                'state': 'count'
            }).rename(columns={'state': 'count'}).reset_index()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_regional_bar = px.bar(
                    regional_efficiency,
                    x='region',
                    y='cost_efficiency_index',
                    color='cost_efficiency_index',
                    color_continuous_scale='Viridis',
                    title='Average Cost Efficiency Index by Region',
                    labels={'cost_efficiency_index': 'Cost Efficiency Index', 'region': 'Region'}
                )
                st.plotly_chart(fig_regional_bar, use_container_width=True)
            
            with col2:
                fig_fuel_idx = px.bar(
                    regional_efficiency,
                    x='region',
                    y='fuel_cost_index',
                    color='fuel_cost_index',
                    color_continuous_scale='RdYlGn_r',
                    title='Average Fuel Cost Index by Region',
                    labels={'fuel_cost_index': 'Fuel Cost Index (1.0=National Avg)', 'region': 'Region'}
                )
                fig_fuel_idx.add_hline(y=1.0, line_dash="dash", line_color="red", 
                                      annotation_text="National Average")
                st.plotly_chart(fig_fuel_idx, use_container_width=True)
            
            # Regional details table
            st.dataframe(regional_efficiency, use_container_width=True, hide_index=True)
    
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
