"""Generate static visualization images for README."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from src.database import get_engine, read_sql_query
from src.analysis.kpis import (
    KPIAnalysis,
    calculate_freight_opportunity_score,
    calculate_logistics_demand_score,
    calculate_fuel_cost_index,
    calculate_cost_efficiency_index,
)

OUTPUT_DIR = Path("docs/images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("Loading engine...")
engine = get_engine()

print("Loading data...")
df_shipping = read_sql_query("SELECT * FROM shipping_stats", engine)
df_fuel = read_sql_query("SELECT * FROM fuel_prices", engine)
df_weather = read_sql_query("SELECT * FROM weather_data", engine)

print(f"  shipping: {len(df_shipping)} rows")
print(f"  fuel: {len(df_fuel)} rows")
print(f"  weather: {len(df_weather)} rows")

df = df_shipping.merge(
    df_fuel[['state', 'regular', 'mid_grade', 'premium', 'diesel']],
    on='state', how='left'
)
if not df_weather.empty:
    df = df.merge(
        df_weather[['state', 'temperature', 'condition', 'humidity', 'wind_speed', 'feels_like']],
        on='state', how='left'
    )

df['population_millions'] = df['population'] / 1_000_000
df['efficiency'] = df['population'] / df['rank']

REGIONS = {
    'Northeast': ['CT','ME','MA','NH','RI','VT','NJ','NY','PA'],
    'South': ['DE','FL','GA','MD','NC','SC','VA','WV','AL','KY','MS','TN','AR','LA','OK','TX'],
    'Midwest': ['IL','IN','MI','OH','WI','IA','KS','MN','MO','NE','ND','SD'],
    'West': ['AZ','CO','ID','MT','NV','NM','UT','WY','AK','CA','HI','OR','WA'],
}
def assign_region(state):
    for region, states in REGIONS.items():
        if state in states:
            return region
    return 'Other'
df['region'] = df['state'].apply(assign_region)

# 1. Population choropleth
print("1/6 Population choropleth...")
fig1 = px.choropleth(
    df, locations='state', locationmode="USA-states",
    color='population_millions', scope="usa",
    color_continuous_scale="Blues",
    title="Population by State (Millions)",
    hover_data=['population','rank','efficiency','diesel']
)
pio.write_image(fig1, OUTPUT_DIR / "population_map.png", width=1000, height=600, scale=2)

# 2. Efficiency choropleth
print("2/6 Efficiency choropleth...")
fig2 = px.choropleth(
    df, locations='state', locationmode="USA-states",
    color='efficiency', scope="usa",
    color_continuous_scale="Viridis",
    title="Efficiency Score by State",
    hover_data=['population','rank','diesel']
)
pio.write_image(fig2, OUTPUT_DIR / "efficiency_map.png", width=1000, height=600, scale=2)

# 3. Diesel prices choropleth
print("3/6 Diesel choropleth...")
fig3 = px.choropleth(
    df, locations='state', locationmode="USA-states",
    color='diesel', scope="usa",
    color_continuous_scale="Reds",
    title="Diesel Prices by State ($)",
    hover_data=['population','rank','efficiency']
)
pio.write_image(fig3, OUTPUT_DIR / "diesel_map.png", width=1000, height=600, scale=2)

# 4. Freight Opportunity choropleth (from KPIs)
print("4/6 Freight opportunity map...")
df_with_kpis = df.copy()
df_with_kpis['freight_opportunity_score'] = calculate_freight_opportunity_score(df_with_kpis)
df_with_kpis['logistics_demand_score'] = calculate_logistics_demand_score(df_with_kpis)
df_with_kpis['fuel_cost_index'] = calculate_fuel_cost_index(df_with_kpis)
df_with_kpis['cost_efficiency_index'] = calculate_cost_efficiency_index(df_with_kpis)

fig4 = px.choropleth(
    df_with_kpis, locations='state', locationmode='USA-states',
    color='freight_opportunity_score', scope='usa',
    color_continuous_scale='RdYlGn',
    title='Freight Opportunity Score by State (0-100)',
    hover_data={'state': True, 'freight_opportunity_score': ':.1f', 'population': ':,.0f', 'diesel': ':.3f'}
)
pio.write_image(fig4, OUTPUT_DIR / "freight_opportunity_map.png", width=1000, height=600, scale=2)

# 5. Diesel vs Logistics Demand scatter
print("5/6 Demand vs Cost scatter...")
fig5 = px.scatter(
    df_with_kpis,
    x='diesel', y='logistics_demand_score',
    size='freight_opportunity_score', color='region',
    hover_name='state',
    title='Diesel Price vs Logistics Demand Score (Size=Opportunity)',
    labels={'diesel': 'Diesel Price (USD/gal)', 'logistics_demand_score': 'Logistics Demand Score'},
    color_discrete_map={'Northeast':'#1f77b4','South':'#ff7f0e','Midwest':'#2ca02c','West':'#d62728'}
)
fig5.update_traces(marker=dict(size=10, opacity=0.7))
pio.write_image(fig5, OUTPUT_DIR / "demand_vs_cost.png", width=1000, height=600, scale=2)

# 6. Correlation heatmap
print("6/6 Correlation heatmap...")
corr_cols = ['population', 'rank', 'efficiency', 'diesel', 'regular']
corr = df_with_kpis[[c for c in corr_cols if c in df_with_kpis.columns]].corr()
fig6 = go.Figure(data=go.Heatmap(
    z=corr.values, x=corr.columns, y=corr.columns,
    colorscale='Viridis', zmin=-1, zmax=1, hoverongaps=False
))
fig6.update_layout(title="Logistics Variables Correlation Matrix", height=500)
pio.write_image(fig6, OUTPUT_DIR / "correlation_heatmap.png", width=800, height=600, scale=2)

print(f"\nDone! {len(list(OUTPUT_DIR.glob('*.png')))} images saved to {OUTPUT_DIR}")
