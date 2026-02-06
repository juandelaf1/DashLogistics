import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys

# --- CONFIGURACIÓN DE RUTAS ---
# Buscamos database.py en el mismo nivel o uno arriba
current_path = Path(__file__).resolve().parent
if (current_path / "database.py").exists():
    sys.path.append(str(current_path))
else:
    sys.path.append(str(current_path.parent))

try:
    from database import get_engine
except ImportError:
    st.error("No se pudo encontrar 'database.py'. Asegúrate de que está en la carpeta 'src'.")
    st.stop()

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DashLogistics BI | Pro", layout="wide", page_icon="📊")

# --- ESTILO CORPORATIVO MEJORADO ---
st.markdown("""
    <style>
    .stApp { background-color: #0b1220; color: #e6eef8; }
    [data-testid="stMetric"] { 
        background-color: #161f30; 
        border-radius: 12px; 
        padding: 20px; 
        border: 1px solid #2d3748;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .stMetric label { color: #94a3b8 !important; font-weight: 600; }
    .stMetric div { color: #60a5fa !important; }
    h1, h2, h3 { color: #60a5fa !important; font-family: 'Inter', sans-serif; }
    .stSidebar { background-color: #071028; border-right: 1px solid #1f2937; }
    </style>
    """, unsafe_allow_html=True)

# --- DICCIONARIO GEOGRÁFICO GLOBAL ---
GEO_DATA = {
    'ALABAMA': {'lat': 32.31, 'lon': -86.90}, 'ALASKA': {'lat': 63.58, 'lon': -154.49},
    'ARIZONA': {'lat': 34.04, 'lon': -111.09}, 'ARKANSAS': {'lat': 35.20, 'lon': -91.83},
    'CALIFORNIA': {'lat': 36.77, 'lon': -119.41}, 'COLORADO': {'lat': 39.55, 'lon': -105.78},
    'FLORIDA': {'lat': 27.66, 'lon': -81.51}, 'TEXAS': {'lat': 31.96, 'lon': -99.90},
    'NEW YORK': {'lat': 40.71, 'lon': -74.00}, 'MICHIGAN': {'lat': 44.31, 'lon': -85.60},
    'ILLINOIS': {'lat': 40.63, 'lon': -89.39}, 'PENNSYLVANIA': {'lat': 41.20, 'lon': -77.19},
    'OHIO': {'lat': 40.41, 'lon': -82.90}, 'GEORGIA': {'lat': 32.15, 'lon': -82.90}
}

# --- LÓGICA DE DATOS ---
@st.cache_data(ttl=60)
def load_and_preprocess(limit=None):
    try:
        engine = get_engine()
        query = "SELECT * FROM master_shipping_data"
        if limit:
            query += f" LIMIT {limit}"
        df = pd.read_sql(query, engine)

        if df.empty:
            return df
        # Normalización
        df.columns = [c.lower() for c in df.columns]
        df['state_up'] = df['state'].str.upper().str.strip()
        
        # Mapeo Geo
        df['lat'] = df['state_up'].map(lambda s: GEO_DATA.get(s, {}).get('lat'))
        df['lon'] = df['state_up'].map(lambda s: GEO_DATA.get(s, {}).get('lon'))
        
        # Métricas Numéricas
        num_cols = ['population', 'diesel', 'current_temp']
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Métrica de Negocio
        df['efficiency'] = df.apply(lambda r: r['population'] / r['diesel'] if r['diesel'] > 0 else 0, axis=1)
        df['cost_index'] = df.apply(lambda r: r['diesel'] / (r['population']/1e6) if r['population'] > 0 else 0, axis=1)
        
        return df
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame()

# --- INTERFAZ ---
st.title("📈 DashLogistics | Operational Intelligence")
st.caption("Perfil: Junior Data Analyst & Scientist | Proyecto: DashLogistics")

# Sidebar
limit_rows = st.sidebar.number_input("Limitar filas (0=Todo)", 0, 1000, 0)
df_raw = load_and_preprocess(limit=limit_rows if limit_rows > 0 else None)

if df_raw.empty:
    st.warning("⚠️ Base de Datos vacía o desconectada. Verifica Docker.")
    st.stop()

# Filtros
all_states = sorted(df_raw['state_up'].unique())
sel_states = st.sidebar.multiselect("Filtrar Estados", all_states, default=all_states)
df_filtered = df_raw[df_raw['state_up'].isin(sel_states)]

# --- KPIs ---
k1, k2, k3, k4 = st.columns(4)
k1.metric("⛽ Diesel Promedio", f"${df_filtered['diesel'].mean():.2f}")
k2.metric("👥 Población Total", f"{df_filtered['population'].sum()/1e6:.1f}M")
k3.metric("🚀 Eficiencia Red", f"{df_filtered['efficiency'].mean()/1e6:.1f}M/$")
k4.metric("🌡️ Temp. Media", f"{df_filtered['current_temp'].mean():.1f}°C")

st.markdown("---")

# --- VISUALIZACIONES ---
row1_left, row1_right = st.columns([2, 1])

with row1_left:
    st.subheader("🗺️ Cobertura Geográfica")
    fig_map = px.scatter_mapbox(
        df_filtered.dropna(subset=['lat', 'lon']), 
        lat="lat", lon="lon", color="diesel", size="population",
        hover_name="state", mapbox_style="carto-positron", 
        color_continuous_scale="RdYlGn_r", zoom=3, height=500
    )
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_map, use_container_width=True)

with row1_right:
    st.subheader("☁️ Condiciones Clima")
    fig_pie = px.pie(df_filtered, names='weather_condition', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_pie.update_layout(showlegend=False, height=500, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_pie, use_container_width=True)

# --- ANÁLISIS DE CORRELACIÓN ---
st.markdown("---")
st.subheader("🔬 Análisis de Correlación: Coste vs Alcance")
g1, g2 = st.columns(2)

with g1:
    fig_scat = px.scatter(df_filtered, x="population", y="diesel", 
                          size="efficiency", color="current_temp",
                          hover_name="state", log_x=True,
                          color_continuous_scale="Viridis", title="Población vs Diesel")
    fig_scat.update_layout(template="plotly_dark")
    st.plotly_chart(fig_scat, use_container_width=True)

with g2:
    # Heatmap simple
    corr = df_filtered[['population', 'diesel', 'current_temp', 'efficiency']].corr()
    fig_heat = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r', title="Matriz de Correlación")
    fig_heat.update_layout(template="plotly_dark")
    st.plotly_chart(fig_heat, use_container_width=True)

# --- TABLA Y EXPORTACIÓN ---
with st.expander("📋 Ver Datos Maestros"):
    st.dataframe(df_filtered.drop(columns=['lat', 'lon']), use_container_width=True)
    st.download_button("Descargar CSV", df_filtered.to_csv(index=False), "data.csv", "text/csv")