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
        if self.df_shipping.empty or 'population' not in self.df_shipping.columns:
            return {}
        
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
        df = self.df_shipping.copy()
        df['population_per_rank'] = df['population'] / df['rank']
        df['rank_per_million_population'] = (df['rank'] / (df['population'] / 1_000_000))

        return {
            'max_efficiency': df['population_per_rank'].max(),
            'min_efficiency': df['population_per_rank'].min(),
            'avg_efficiency': df['population_per_rank'].mean(),
            'avg_efficiency_score': df['population_per_rank'].mean(),  
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


# ==============================================================================
# Pure, reusable KPI calculation functions for logistics operations
# ==============================================================================

def calculate_fuel_cost_index(df: pd.DataFrame, diesel_col: str = 'diesel') -> pd.Series:
    """
    Calculate Fuel Cost Index for each state.
    
    Compares each state's diesel price with the national average.
    Index > 1.0 means diesel is more expensive than average.
    Index < 1.0 means diesel is cheaper than average.
    
    Business meaning: Identifies states with premium/discounted fuel costs.
    Useful for adjusting logistics rates and cost projections.
    
    Formula:
        fuel_cost_index = diesel_price / mean(diesel_price)
    
    Args:
        df: DataFrame with diesel price column
        diesel_col: Name of diesel price column (default: 'diesel')
    
    Returns:
        pd.Series with fuel_cost_index values
    
    Example:
        >>> df['fuel_cost_index'] = calculate_fuel_cost_index(df)
        >>> high_cost = df[df['fuel_cost_index'] > 1.1]  # 10% above average
    """
    mean_diesel = df[diesel_col].mean()
    return df[diesel_col] / mean_diesel


def calculate_logistics_demand_score(
    df: pd.DataFrame,
    population_col: str = 'population',
    population_density_col: str = None,
    land_area_col: str = None
) -> pd.Series:
    """
    Calculate Logistics Demand Score for each state.
    
    Proxy metric for logistics demand, combining population size with density.
    Higher score indicates greater absolute demand for logistics services.
    
    Business meaning: Identifies states with high logistics activity potential.
    Useful for warehouse location selection and service capacity planning.
    
    Formula:
        logistics_demand_score = population * population_density
    
    If population_density not provided, approximates using:
        population_density = population / land_area
    
    Args:
        df: DataFrame with required columns
        population_col: Name of population column (default: 'population')
        population_density_col: Name of population density column (optional)
        land_area_col: Name of land area column (used if density unavailable)
    
    Returns:
        pd.Series with logistics_demand_score values
    
    Example:
        >>> df['logistics_demand_score'] = calculate_logistics_demand_score(df)
        >>> high_demand = df.nlargest(10, 'logistics_demand_score')
    """
    population = df[population_col]
    
    if population_density_col and population_density_col in df.columns:
        # Use provided population density
        population_density = df[population_density_col]
    elif land_area_col and land_area_col in df.columns:
        # Calculate density from land area
        population_density = population / df[land_area_col]
    else:
        # TODO: Integrate land_area data from US Census Bureau or similar source
        # For now, approximate logistics demand score with population as proxy
        # In production, this should use actual land area data for state-level calculations
        population_density = population / 1000  # Simplified approximation
    
    return population * population_density


def calculate_freight_opportunity_score(
    df: pd.DataFrame,
    weights: Dict = None,
    population_col: str = 'population',
    population_density_col: str = None,
    land_area_col: str = None,
    diesel_col: str = 'diesel'
) -> pd.Series:
    """
    Calculate Freight Opportunity Score for each state.
    
    Composite metric estimating logistics expansion potential.
    Combines normalized population, population density, and inverted diesel costs.
    Score scaled between 0–100 for easy interpretation.
    
    Business meaning: Identifies high-potential markets for logistics expansion.
    States with higher scores have favorable demographics + lower fuel costs.
    
    Formula:
        freight_opportunity_score = 
          0.4 * normalized_population +
          0.3 * normalized_population_density +
          0.3 * inverse_diesel_price
        
        Scaled to 0-100 range
    
    Args:
        df: DataFrame with required columns
        weights: Dict with keys 'population', 'density', 'fuel_cost' (optional)
                Default: {'population': 0.4, 'density': 0.3, 'fuel_cost': 0.3}
        population_col: Name of population column (default: 'population')
        population_density_col: Name of population density column (optional)
        land_area_col: Name of land area column (used if density unavailable)
        diesel_col: Name of diesel price column (default: 'diesel')
    
    Returns:
        pd.Series with freight_opportunity_score values (0-100)
    
    Example:
        >>> df['freight_opportunity_score'] = calculate_freight_opportunity_score(df)
        >>> best_opportunities = df.nlargest(5, 'freight_opportunity_score')
    """
    if weights is None:
        weights = {
            'population': 0.4,
            'density': 0.3,
            'fuel_cost': 0.3
        }
    
    # Normalize population (min-max scaling to 0-1)
    population = df[population_col]
    pop_min = population.min()
    pop_max = population.max()
    normalized_population = (population - pop_min) / (pop_max - pop_min) if pop_max > pop_min else population / pop_max
    
    # Calculate or get population density
    if population_density_col and population_density_col in df.columns:
        population_density = df[population_density_col]
    elif land_area_col and land_area_col in df.columns:
        population_density = population / df[land_area_col]
    else:
        # TODO: Integrate land_area data from US Census Bureau
        population_density = population / 1000  # Simplified approximation
    
    # Normalize density (min-max scaling to 0-1)
    density_min = population_density.min()
    density_max = population_density.max()
    normalized_density = (population_density - density_min) / (density_max - density_min) if density_max > density_min else population_density / density_max
    
    # Invert diesel prices (lower price = higher score)
    diesel_prices = df[diesel_col]
    diesel_max = diesel_prices.max()
    inverted_diesel = (diesel_max - diesel_prices) / (diesel_max - diesel_prices.min()) if diesel_max > diesel_prices.min() else (diesel_max - diesel_prices) / diesel_max
    
    # Calculate composite score
    composite_score = (
        weights['population'] * normalized_population +
        weights['density'] * normalized_density +
        weights['fuel_cost'] * inverted_diesel
    )
    
    # Scale to 0-100
    return composite_score * 100


def calculate_cost_efficiency_index(
    df: pd.DataFrame,
    population_col: str = 'population',
    population_density_col: str = None,
    land_area_col: str = None,
    diesel_col: str = 'diesel'
) -> pd.Series:
    """
    Calculate Cost Efficiency Index for each state.
    
    Composite metric measuring logistics market efficiency.
    Ratio of logistics demand (population × density) to diesel cost.
    Higher value indicates better logistics market efficiency.
    
    Business meaning: Markets where high demand is served with lower fuel costs.
    Useful for identifying optimal locations for cost-efficient operations.
    
    Formula:
        cost_efficiency_index = logistics_demand_score / diesel_price
    
    Args:
        df: DataFrame with required columns
        population_col: Name of population column (default: 'population')
        population_density_col: Name of population density column (optional)
        land_area_col: Name of land area column (used if density unavailable)
        diesel_col: Name of diesel price column (default: 'diesel')
    
    Returns:
        pd.Series with cost_efficiency_index values
    
    Example:
        >>> df['cost_efficiency_index'] = calculate_cost_efficiency_index(df)
        >>> efficient_markets = df.nlargest(10, 'cost_efficiency_index')
        >>> print(f"Cost efficiency range: {df['cost_efficiency_index'].min():.2f} - {df['cost_efficiency_index'].max():.2f}")
    """
    demand_score = calculate_logistics_demand_score(
        df,
        population_col=population_col,
        population_density_col=population_density_col,
        land_area_col=land_area_col
    )
    
    diesel_prices = df[diesel_col]
    
    # Avoid division by zero
    return demand_score / diesel_prices.replace(0, np.nan)
