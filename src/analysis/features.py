# src/analysis/features.py
import pandas as pd
import numpy as np
from typing import Dict, List

class FeatureEngineering:
    """Feature engineering para DashLogistics"""
    
    def __init__(self, df_shipping: pd.DataFrame, df_fuel: pd.DataFrame = None):
        self.df_shipping = df_shipping.copy()
        self.df_fuel = df_fuel.copy() if df_fuel is not None else None
        
    def create_basic_features(self) -> pd.DataFrame:
        """Crear features básicas"""
        df = self.df_shipping.copy()
        
        # Ratios y eficiencia
        df['population_per_rank'] = df['population'] / df['rank']
        df['rank_per_population'] = df['rank'] / df['population']
        df['efficiency_score'] = df['population'] / (df['rank'] * 1000)
        
        # Log transformations
        df['log_population'] = np.log(df['population'])
        df['log_rank'] = np.log(df['rank'])
        
        return df
    
    def create_regional_features(self) -> pd.DataFrame:
        """Crear features regionales"""
        df = self.df_shipping.copy()
        
        # Definir regiones por códigos postales
        regions = {
            'Northeast': ['CT', 'ME', 'MA', 'NH', 'RI', 'VT', 'NJ', 'NY', 'PA'],
            'Midwest': ['IL', 'IN', 'MI', 'OH', 'WI', 'IA', 'KS', 'MN', 'MO', 'NE', 'ND', 'SD'],
            'South': ['DE', 'FL', 'GA', 'MD', 'NC', 'SC', 'VA', 'DC', 'WV', 'AL', 'KY', 'MS', 'TN', 'AR', 'LA', 'OK', 'TX'],
            'West': ['AZ', 'CO', 'ID', 'MT', 'NV', 'NM', 'UT', 'WY', 'AK', 'CA', 'HI', 'OR', 'WA']
        }
        
        # Asignar región
        def get_region(postal):
            for region, states in regions.items():
                if postal in states:
                    return region
            return 'Other'
        
        df['region'] = df['postal'].apply(get_region)
        
        # Features regionales
        region_stats = df.groupby('region')['population'].agg(['mean', 'std']).to_dict('index')
        df['region_population_mean'] = df['region'].map(region_stats['mean'])
        df['region_population_std'] = df['region'].map(region_stats['std'])
        
        return df
    
    def create_fuel_features(self) -> pd.DataFrame:
        """Crear features con datos de combustible"""
        if self.df_fuel is None:
            return self.df_shipping
            
        # Merge con datos de combustible
        df = self.df_shipping.merge(self.df_fuel[['state', 'regular', 'diesel']], 
                                  on='state', how='left')
        
        # Features de combustible
        df['fuel_efficiency'] = df['population'] / df['diesel']
        df['fuel_cost_per_capita'] = df['diesel'] / df['population'] * 1000
        df['fuel_affordability_index'] = (df['population'] / df['diesel']) * 100
        
        return df
    
    def create_statistical_features(self) -> pd.DataFrame:
        """Crear features estadísticas"""
        df = self.df_shipping.copy()
        
        # Percentiles
        df['population_percentile'] = df['population'].rank(pct=True)
        df['rank_percentile'] = df['rank'].rank(pct=True)
        
        # Z-scores
        df['population_zscore'] = (df['population'] - df['population'].mean()) / df['population'].std()
        df['rank_zscore'] = (df['rank'] - df['rank'].mean()) / df['rank'].std()
        
        return df
    
    def create_composite_features(self) -> pd.DataFrame:
        """Crear features compuestas"""
        df = self.df_shipping.copy()
        
        # Índices compuestos
        df['logistics_index'] = (df['population'] / df['rank']) * 0.5 + \
                               (df['population'] / 1000000) * 0.3 + \
                               (100 - df['rank']) * 0.2
        
        df['development_score'] = np.log(df['population']) * 0.6 + \
                               (100 - df['rank']) * 0.4
        
        return df
    
    def get_all_features(self) -> pd.DataFrame:
        """Obtener todas las features"""
        df = self.df_shipping.copy()
        
        # Aplicar todas las transformaciones
        df = self.create_basic_features()
        df = self.create_regional_features()
        df = self.create_statistical_features()
        df = self.create_composite_features()
        
        if self.df_fuel is not None:
            df = self.create_fuel_features()
        
        return df
    
    def get_feature_summary(self) -> Dict:
        """Resumen de features creadas"""
        features = {
            'basic_features': ['population_per_rank', 'efficiency_score', 'log_population', 'log_rank'],
            'regional_features': ['region', 'region_population_mean', 'region_population_std'],
            'statistical_features': ['population_percentile', 'rank_percentile', 'population_zscore', 'rank_zscore'],
            'composite_features': ['logistics_index', 'development_score'],
            'fuel_features': ['fuel_efficiency', 'fuel_cost_per_capita', 'fuel_affordability_index'] if self.df_fuel is not None else []
        }
        
        total_features = []
        for feature_list in features.values():
            total_features.extend(feature_list)
        
        return {
            'features_by_type': features,
            'total_features': total_features,
            'feature_count': len(total_features)
        }
