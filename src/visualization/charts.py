# src/visualization/charts.py
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple
import seaborn as sns

class AdvancedCharts:
    """Visualizaciones avanzadas para DashLogistics"""
    
    def __init__(self, df: pd.DataFrame, df_fuel: pd.DataFrame = None):
        self.df = df.copy()
        self.df_fuel = df_fuel.copy() if df_fuel is not None else None
        self.colors = px.colors.qualitative.Set3
    
    def create_correlation_heatmap(self, corr_matrix: pd.DataFrame) -> go.Figure:
        """Crear heatmap de correlaciones mejorado"""
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False,
            colorbar=dict(title="Correlation")
        ))
        
        fig.update_layout(
            title='Correlation Matrix - Shipping Data Analysis',
            xaxis_title='Variables',
            yaxis_title='Variables',
            width=700,
            height=600,
            font=dict(size=12)
        )
        
        return fig
    
    def create_distribution_plots(self, columns: List[str]) -> List[go.Figure]:
        """Crear múltiples gráficos de distribución"""
        figures = []
        
        for i, col in enumerate(columns[:4]):  # Limitar a 4 gráficos
            if col in self.df.columns:
                data = self.df[col].dropna()
                
                fig = go.Figure()
                
                # Histograma
                fig.add_trace(go.Histogram(
                    x=data,
                    name=col,
                    nbinsx=30,
                    opacity=0.7,
                    marker_color=self.colors[i % len(self.colors)],
                    hovertemplate=f'<b>{col}</b><br>Value: %{{x}}<br>Count: %{{y}}'
                ))
                
                # Líneas estadísticas
                mean_val = data.mean()
                median_val = data.median()
                
                fig.add_vline(
                    x=mean_val, 
                    line_dash="dash", 
                    line_color="red", 
                    annotation_text=f"Mean: {mean_val:.2f}",
                    annotation_position="top right"
                )
                
                fig.add_vline(
                    x=median_val, 
                    line_dash="dot", 
                    line_color="green", 
                    annotation_text=f"Median: {median_val:.2f}",
                    annotation_position="top left"
                )
                
                fig.update_layout(
                    title=f'Distribution of {col}',
                    xaxis_title=col,
                    yaxis_title='Frequency',
                    showlegend=False,
                    height=400,
                    font=dict(size=11)
                )
                
                figures.append(fig)
        
        return figures
    
    def create_scatter_analysis(self, x_col: str, y_col: str, 
                           color_col: str = None, size_col: str = None) -> go.Figure:
        """Crear scatter plot avanzado"""
        fig = go.Figure()
        
        # Scatter plot principal
        fig.add_trace(go.Scatter(
            x=self.df[x_col],
            y=self.df[y_col],
            mode='markers',
            marker=dict(
                size=self.df[size_col] if size_col else 10,
                color=self.df[color_col] if color_col else self.df[y_col],
                colorscale='Viridis',
                showscale=True if color_col else False,
                colorbar=dict(title=color_col) if color_col else None,
                line=dict(width=1, color='white')
            ),
            text=self.df['state'],
            hovertemplate='<b>%{text}</b><br>' + 
                       f'<b>{x_col}:</b> %{{x}}<br>' +
                       f'<b>{y_col}:</b> %{{y}}',
            name='States'
        ))
        
        # Línea de tendencia
        fig.add_trace(go.Scatter(
            x=self.df[x_col],
            y=np.polyfit(self.df[x_col], self.df[y_col], 1)[0] * self.df[x_col] + 
                   np.polyfit(self.df[x_col], self.df[y_col], 1)[1],
            mode='lines',
            name='Trend Line',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        fig.update_layout(
            title=f'{y_col.replace("_", " ").title()} vs {x_col.replace("_", " ").title()}',
            xaxis_title=x_col.replace("_", " ").title(),
            yaxis_title=y_col.replace("_", " ").title(),
            height=500,
            font=dict(size=12)
        )
        
        return fig
    
    def create_box_plots_by_region(self, numeric_col: str) -> go.Figure:
        """Crear box plots por región"""
        if 'region' not in self.df.columns:
            return go.Figure()
        
        fig = go.Figure()
        
        regions = self.df['region'].unique()
        for i, region in enumerate(regions):
            region_data = self.df[self.df['region'] == region][numeric_col]
            
            fig.add_trace(go.Box(
                y=region_data,
                name=region,
                marker_color=self.colors[i % len(self.colors)],
                boxpoints='outliers'
            ))
        
        fig.update_layout(
            title=f'{numeric_col.replace("_", " ").title()} by Region',
            xaxis_title='Region',
            yaxis_title=numeric_col.replace("_", " ").title(),
            height=500,
            font=dict(size=12),
            showlegend=True
        )
        
        return fig
    
    def create_regional_comparison_chart(self) -> go.Figure:
        """Crear gráfico comparativo por región"""
        if 'region' not in self.df.columns:
            return go.Figure()
        
        # Calcular estadísticas por región
        regional_stats = self.df.groupby('region').agg({
            'population': ['sum', 'mean', 'std'],
            'rank': ['mean', 'min']
        }).round(2)
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Total Population by Region',
                'Average Population by Region',
                'Average Rank by Region',
                'Population Distribution'
            ],
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Total población
        fig.add_trace(
            go.Bar(
                x=regional_stats.index,
                y=regional_stats[('population', 'sum')],
                name='Total Population',
                marker_color=self.colors[0]
            ),
            row=1, col=1
        )
        
        # Promedio población
        fig.add_trace(
            go.Bar(
                x=regional_stats.index,
                y=regional_stats[('population', 'mean')],
                name='Avg Population',
                marker_color=self.colors[1]
            ),
            row=1, col=2
        )
        
        # Promedio rank
        fig.add_trace(
            go.Bar(
                x=regional_stats.index,
                y=regional_stats[('rank', 'mean')],
                name='Avg Rank',
                marker_color=self.colors[2]
            ),
            row=2, col=1
        )
        
        # Distribución (pie chart)
        fig.add_trace(
            go.Pie(
                labels=regional_stats.index,
                values=regional_stats[('population', 'sum')],
                name='Population Share',
                marker_colors=self.colors[:len(regional_stats)]
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=700,
            title_text="Regional Analysis Dashboard",
            showlegend=False,
            font=dict(size=11)
        )
        
        return fig
    
    def create_fuel_analysis_charts(self) -> List[go.Figure]:
        """Crear gráficos de análisis de combustible"""
        if self.df_fuel is None:
            return []
        
        figures = []
        
        # 1. Comparación de precios
        fig1 = go.Figure()
        fuel_types = ['regular', 'mid_grade', 'premium', 'diesel']
        
        for fuel_type in fuel_types:
            fig1.add_trace(go.Box(
                y=self.df_fuel[fuel_type],
                name=fuel_type.replace('_', ' ').title(),
                marker_color=self.colors[fuel_types.index(fuel_type)]
            ))
        
        fig1.update_layout(
            title='Fuel Price Distribution by Type',
            xaxis_title='Fuel Type',
            yaxis_title='Price ($)',
            height=400,
            font=dict(size=11)
        )
        figures.append(fig1)
        
        # 2. Precios por estado (top 15)
        fig2 = go.Figure()
        top_states = self.df_fuel.nlargest(15, 'regular')
        
        fig2.add_trace(go.Bar(
            x=top_states['state'],
            y=top_states['regular'],
            name='Regular Price',
            marker_color=self.colors[0]
        ))
        
        fig2.update_layout(
            title='Regular Fuel Prices - Top 15 States',
            xaxis_title='State',
            yaxis_title='Price ($)',
            height=400,
            font=dict(size=11)
        )
        figures.append(fig2)
        
        # 3. Correlación precios
        fig3 = go.Figure()
        corr_matrix = self.df_fuel[['regular', 'mid_grade', 'premium', 'diesel']].corr()
        
        fig3.add_trace(go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='Viridis',
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10}
        ))
        
        fig3.update_layout(
            title='Fuel Price Correlation Matrix',
            height=400,
            font=dict(size=11)
        )
        figures.append(fig3)
        
        return figures
    
    def create_kpi_dashboard(self, kpis: Dict) -> go.Figure:
        """Crear dashboard de KPIs"""
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=[
                'Population Metrics',
                'Rank Metrics', 
                'Efficiency Metrics',
                'Regional Distribution',
                'Data Quality',
                'Performance Index'
            ],
            specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
                   [{"type": "pie"}, {"type": "indicator"}, {"type": "indicator"}]]
        )
        
        # KPIs de población
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=kpis.get('total_population', 0),
                title={"text": "Total Population"},
                number={'valueformat': ','}
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=kpis.get('avg_population', 0),
                title={"text": "Avg Population"},
                number={'valueformat': ','}
            ),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=kpis.get('avg_efficiency', 0),
                title={"text": "Avg Efficiency"},
                number={'valueformat': '.2f'}
            ),
            row=1, col=3
        )
        
        # KPIs de rank
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=kpis.get('avg_rank', 0),
                title={"text": "Average Rank"},
                number={'valueformat': '.1f'}
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=kpis.get('max_efficiency', 0),
                title={"text": "Max Efficiency"},
                number={'valueformat': '.2f'}
            ),
            row=2, col=2
        )
        
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=kpis.get('data_completeness', 0),
                title={"text": "Data Quality %"},
                number={'valueformat': '.1f'}
            ),
            row=2, col=3
        )
        
        fig.update_layout(
            height=600,
            title_text="KPIs Dashboard",
            font=dict(size=11)
        )
        
        return fig
    
    def create_comprehensive_analysis_dashboard(self) -> Dict[str, go.Figure]:
        """Crear dashboard completo de análisis"""
        charts = {}
        
        # Correlation heatmap
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_matrix = self.df[numeric_cols].corr()
            charts['correlation'] = self.create_correlation_heatmap(corr_matrix)
        
        # Distribution plots
        charts['distributions'] = self.create_distribution_plots(numeric_cols.tolist())
        
        # Regional analysis
        charts['regional'] = self.create_regional_comparison_chart()
        
        # Fuel analysis
        if self.df_fuel is not None:
            charts['fuel'] = self.create_fuel_analysis_charts()
        
        return charts
