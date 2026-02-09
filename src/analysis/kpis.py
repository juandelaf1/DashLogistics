# src/analysis/kpis.py
import pandas as pd
import numpy as np
from typing import Dict, List

class KPIAnalysis:
    """Cálculo de KPIs avanzados para DashLogistics"""
    
    def __init__(self, df_shipping: pd.DataFrame, df_fuel: pd.DataFrame = None):
        self.df_shipping = df_shipping.copy()
        self.df_fuel = df_fuel.copy() if df_fuel is not None else None
    
    def basic_kpis(self) -> Dict:
        """KPIs básicos del dataset"""
        return {
            'total_states': len(self.df_shipping),
            'total_population': self.df_shipping['population'].sum(),
            'avg_population': self.df_shipping['population'].mean(),
            'median_population': self.df_shipping['population'].median(),
            'population_std': self.df_shipping['population'].std(),
            'avg_rank': self.df_shipping['rank'].mean(),
            'median_rank': self.df_shipping['rank'].median(),
            'rank_std': self.df_shipping['rank'].std()
        }
    
    def efficiency_kpis(self) -> Dict:
        """KPIs de eficiencia"""
        df = self.df_shipping.copy()
        
        # Métricas de eficiencia
        df['population_per_rank'] = df['population'] / df['rank']
        df['rank_per_million_population'] = (df['rank'] / (df['population'] / 1000000))
        
        return {
            'max_efficiency': df['population_per_rank'].max(),
            'min_efficiency': df['population_per_rank'].min(),
            'avg_efficiency': df['population_per_rank'].mean(),
            'efficiency_std': df['population_per_rank'].std(),
            'best_rank_per_million': df['rank_per_million_population'].min(),
            'worst_rank_per_million': df['rank_per_million_population'].max()
        }
    
    def distribution_kpis(self) -> Dict:
        """KPIs de distribución"""
        df = self.df_shipping.copy()
        
        # Percentiles
        pop_90 = df['population'].quantile(0.9)
        pop_10 = df['population'].quantile(0.1)
        rank_90 = df['rank'].quantile(0.9)
        rank_10 = df['rank'].quantile(0.1)
        
        return {
            'population_90th_percentile': pop_90,
            'population_10th_percentile': pop_10,
            'population_ratio_90_10': pop_90 / pop_10,
            'rank_90th_percentile': rank_90,
            'rank_10th_percentile': rank_10,
            'rank_ratio_90_10': rank_90 / rank_10,
            'top_10_percent_population_share': df[df['population'] >= pop_90]['population'].sum() / df['population'].sum() * 100
        }
    
    def fuel_kpis(self) -> Dict:
        """KPIs de combustible"""
        if self.df_fuel is None:
            return {}
        
        df = self.df_fuel.copy()
        
        return {
            'avg_regular_price': df['regular'].mean(),
            'median_regular_price': df['regular'].median(),
            'regular_price_std': df['regular'].std(),
            'avg_diesel_price': df['diesel'].mean(),
            'median_diesel_price': df['diesel'].median(),
            'diesel_price_std': df['diesel'].std(),
            'regular_price_range': df['regular'].max() - df['regular'].min(),
            'diesel_price_range': df['diesel'].max() - df['diesel'].min(),
            'price_volatility_regular': df['regular'].std() / df['regular'].mean(),
            'price_volatility_diesel': df['diesel'].std() / df['diesel'].mean()
        }
    
    def regional_kpis(self) -> Dict:
        """KPIs regionales"""
        df = self.df_shipping.copy()
        
        if 'region' not in df.columns:
            return {}
        
        regional_stats = {}
        for region in df['region'].unique():
            region_data = df[df['region'] == region]
            
            regional_stats[region] = {
                'state_count': len(region_data),
                'total_population': region_data['population'].sum(),
                'avg_population': region_data['population'].mean(),
                'avg_rank': region_data['rank'].mean(),
                'population_share': region_data['population'].sum() / df['population'].sum() * 100,
                'best_state_rank': region_data.loc[region_data['rank'].idxmin(), 'state'] if not region_data.empty else None,
                'best_rank_value': region_data['rank'].min() if not region_data.empty else None
            }
        
        return regional_stats
    
    def composite_kpis(self) -> Dict:
        """KPIs compuestos"""
        df = self.df_shipping.copy()
        
        # Índices compuestos
        df['logistics_performance_index'] = (
            (df['population'] / df['population'].max()) * 0.4 +
            (1 - df['rank'] / df['rank'].max()) * 0.6
        ) * 100
        
        df['development_index'] = (
            np.log(df['population']) / np.log(df['population'].max()) * 0.5 +
            (1 - df['rank'] / df['rank'].max()) * 0.5
        ) * 100
        
        return {
            'top_logistics_performer': df.loc[df['logistics_performance_index'].idxmax(), 'state'],
            'top_logistics_score': df['logistics_performance_index'].max(),
            'bottom_logistics_performer': df.loc[df['logistics_performance_index'].idxmin(), 'state'],
            'bottom_logistics_score': df['logistics_performance_index'].min(),
            'top_developer': df.loc[df['development_index'].idxmax(), 'state'],
            'top_development_score': df['development_index'].max(),
            'bottom_developer': df.loc[df['development_index'].idxmin(), 'state'],
            'bottom_development_score': df['development_index'].min()
        }
    
    def quality_kpis(self) -> Dict:
        """KPIs de calidad de datos"""
        df = self.df_shipping.copy()
        
        return {
            'data_completeness': (1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100,
            'duplicate_states': df['state'].duplicated().sum(),
            'unique_states': df['state'].nunique(),
            'population_outliers': len(self._detect_outliers_iqr(df['population'])),
            'rank_outliers': len(self._detect_outliers_iqr(df['rank'])),
            'data_consistency_score': self._calculate_consistency_score(df)
        }
    
    def _detect_outliers_iqr(self, series: pd.Series) -> List:
        """Detectar outliers usando IQR"""
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        return series[(series < lower_bound) | (series > upper_bound)].index.tolist()
    
    def _calculate_consistency_score(self, df: pd.DataFrame) -> float:
        """Calcular score de consistencia de datos"""
        score = 100
        
        # Verificar rangos lógicos
        if df['population'].min() < 0:
            score -= 20
        if df['rank'].min() < 1:
            score -= 20
        
        # Verificar duplicados
        if df['state'].duplicated().any():
            score -= 10
        
        return max(score, 0)
    
    def get_all_kpis(self) -> Dict:
        """Obtener todos los KPIs"""
        all_kpis = {}
        
        all_kpis.update(self.basic_kpis())
        all_kpis.update(self.efficiency_kpis())
        all_kpis.update(self.distribution_kpis())
        all_kpis.update(self.fuel_kpis())
        all_kpis.update(self.regional_kpis())
        all_kpis.update(self.composite_kpis())
        all_kpis.update(self.quality_kpis())
        
        return all_kpis
    
    def get_kpi_summary(self) -> Dict:
        """Resumen de KPIs"""
        all_kpis = self.get_all_kpis()
        
        return {
            'total_kpis': len(all_kpis),
            'kpi_categories': {
                'basic': list(self.basic_kpis().keys()),
                'efficiency': list(self.efficiency_kpis().keys()),
                'distribution': list(self.distribution_kpis().keys()),
                'fuel': list(self.fuel_kpis().keys()) if self.df_fuel is not None else [],
                'regional': list(self.regional_kpis().keys()),
                'composite': list(self.composite_kpis().keys()),
                'quality': list(self.quality_kpis().keys())
            },
            'key_insights': self._generate_kpi_insights(all_kpis)
        }
    
    def _generate_kpi_insights(self, kpis: Dict) -> List[str]:
        """Generar insights basados en KPIs"""
        insights = []
        
        if 'avg_efficiency' in kpis:
            insights.append(f"Average efficiency score: {kpis['avg_efficiency']:,.2f}")
        
        if 'population_90th_percentile' in kpis and 'population_10th_percentile' in kpis:
            ratio = kpis['population_90th_percentile'] / kpis['population_10th_percentile']
            insights.append(f"Population disparity: Top 10% have {ratio:.1f}x more population than bottom 10%")
        
        if 'regional_kpis' in kpis and kpis['regional_kpis']:
            max_region = max(kpis['regional_kpis'].keys(), 
                          key=lambda x: kpis['regional_kpis'][x]['total_population'])
            insights.append(f"Largest region by population: {max_region}")
        
        return insights
