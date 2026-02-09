# src/analysis/eda.py
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from typing import Dict, List, Tuple

class EDAAnalysis:
    """Análisis Exploratorio de Datos para DashLogistics"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    def descriptive_statistics(self) -> Dict:
        """Estadísticas descriptivas completas"""
        stats_dict = {}
        
        for col in self.numeric_cols:
            data = self.df[col].dropna()
            stats_dict[col] = {
                'count': len(data),
                'mean': data.mean(),
                'median': data.median(),
                'std': data.std(),
                'var': data.var(),
                'min': data.min(),
                'max': data.max(),
                'q25': data.quantile(0.25),
                'q75': data.quantile(0.75),
                'iqr': data.quantile(0.75) - data.quantile(0.25),
                'skewness': stats.skew(data),
                'kurtosis': stats.kurtosis(data),
                'cv': data.std() / data.mean() if data.mean() != 0 else 0
            }
        
        return stats_dict
    
    def correlation_analysis(self) -> Tuple[pd.DataFrame, Dict]:
        """Análisis de correlación"""
        # Matriz de correlación
        corr_matrix = self.df[self.numeric_cols].corr()
        
        # Encontrar correlaciones fuertes
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.5:  # Correlación moderada-fuerte
                    strong_correlations.append({
                        'var1': corr_matrix.columns[i],
                        'var2': corr_matrix.columns[j],
                        'correlation': corr_val,
                        'strength': 'Strong' if abs(corr_val) > 0.7 else 'Moderate'
                    })
        
        return corr_matrix, strong_correlations
    
    def distribution_analysis(self) -> Dict:
        """Análisis de distribuciones"""
        dist_analysis = {}
        
        for col in self.numeric_cols:
            data = self.df[col].dropna()
            
            # Test de normalidad
            if len(data) > 3:
                shapiro_stat, shapiro_p = stats.shapiro(data[:5000])  # Limitar a 5000 muestras
                normality_test = 'Normal' if shapiro_p > 0.05 else 'Not Normal'
            else:
                shapiro_stat, shapiro_p, normality_test = None, None, 'Insufficient data'
            
            dist_analysis[col] = {
                'distribution_type': normality_test,
                'shapiro_stat': shapiro_stat,
                'shapiro_p_value': shapiro_p,
                'outliers_count': len(self.detect_outliers_iqr(col)),
                'outlier_percentage': len(self.detect_outliers_iqr(col)) / len(data) * 100
            }
        
        return dist_analysis
    
    def detect_outliers_iqr(self, column: str) -> List:
        """Detectar outliers usando método IQR"""
        data = self.df[column].dropna()
        q1 = data.quantile(0.25)
        q3 = data.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = data[(data < lower_bound) | (data > upper_bound)]
        return outliers.index.tolist()
    
    def regional_analysis(self) -> Dict:
        """Análisis por regiones"""
        if 'region' not in self.df.columns:
            return {}
        
        regional_stats = {}
        for region in self.df['region'].unique():
            region_data = self.df[self.df['region'] == region]
            
            regional_stats[region] = {
                'count': len(region_data),
                'avg_population': region_data['population'].mean(),
                'avg_rank': region_data['rank'].mean(),
                'total_population': region_data['population'].sum(),
                'population_std': region_data['population'].std(),
                'best_rank': region_data['rank'].min(),
                'worst_rank': region_data['rank'].max()
            }
        
        return regional_stats
    
    def create_correlation_heatmap(self) -> go.Figure:
        """Crear heatmap de correlaciones"""
        corr_matrix, _ = self.correlation_analysis()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.round(2).values,
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='Correlation Matrix',
            xaxis_title='Variables',
            yaxis_title='Variables',
            width=600,
            height=600
        )
        
        return fig
    
    def create_distribution_plots(self) -> List[go.Figure]:
        """Crear gráficos de distribución"""
        figures = []
        
        for col in self.numeric_cols[:4]:  # Limitar a primeras 4 columnas
            data = self.df[col].dropna()
            
            # Histograma
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=data,
                name=col,
                nbinsx=30,
                opacity=0.7
            ))
            
            # Añadir línea de media y mediana
            fig.add_vline(x=data.mean(), line_dash="dash", line_color="red", 
                         annotation_text=f"Mean: {data.mean():.2f}")
            fig.add_vline(x=data.median(), line_dash="dash", line_color="green", 
                         annotation_text=f"Median: {data.median():.2f}")
            
            fig.update_layout(
                title=f'Distribution of {col}',
                xaxis_title=col,
                yaxis_title='Frequency',
                showlegend=False
            )
            
            figures.append(fig)
        
        return figures
    
    def create_scatter_matrix(self) -> go.Figure:
        """Crear scatter plot matrix"""
        # Seleccionar columnas principales
        main_cols = ['population', 'rank'] + [col for col in self.numeric_cols if col not in ['population', 'rank']][:2]
        
        if len(main_cols) < 2:
            return go.Figure()
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=main_cols[:4],
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Añadir scatter plots
        for i, col in enumerate(main_cols[:4]):
            row = i // 2 + 1
            col_idx = i % 2 + 1
            
            fig.add_trace(
                go.Scatter(
                    x=self.df['population'],
                    y=self.df[col],
                    mode='markers',
                    name=col,
                    text=self.df['state'],
                    showlegend=False
                ),
                row=row, col=col_idx
            )
        
        fig.update_layout(height=600, title_text="Scatter Plot Matrix")
        return fig
    
    def generate_insights(self) -> List[str]:
        """Generar insights automáticos"""
        insights = []
        
        # Insights de población
        pop_stats = self.descriptive_statistics()['population']
        insights.append(f"Population ranges from {pop_stats['min']:,.0f} to {pop_stats['max']:,.0f}")
        insights.append(f"Average population is {pop_stats['mean']:,.0f} with CV of {pop_stats['cv']:.2f}")
        
        # Insights de correlación
        _, strong_corr = self.correlation_analysis()
        if strong_corr:
            insights.append(f"Found {len(strong_corr)} strong correlations between variables")
            for corr in strong_corr[:3]:
                insights.append(f"Strong correlation: {corr['var1']} vs {corr['var2']} ({corr['correlation']:.2f})")
        
        # Insights regionales
        regional_stats = self.regional_analysis()
        if regional_stats:
            max_region = max(regional_stats.keys(), key=lambda x: regional_stats[x]['avg_population'])
            insights.append(f"Region with highest average population: {max_region}")
        
        return insights
    
    def get_eda_summary(self) -> Dict:
        """Resumen completo del EDA"""
        return {
            'dataset_shape': self.df.shape,
            'numeric_columns': self.numeric_cols,
            'categorical_columns': self.categorical_cols,
            'missing_values': self.df.isnull().sum().to_dict(),
            'descriptive_stats': self.descriptive_statistics(),
            'correlations': self.correlation_analysis()[1],
            'distributions': self.distribution_analysis(),
            'regional_analysis': self.regional_analysis(),
            'insights': self.generate_insights()
        }
