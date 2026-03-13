"""
Unit tests for KPI and Feature Analysis modules.
Tests for src/analysis/kpis.py and src/analysis/features.py
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

# Import analysis modules
from src.analysis.kpis import KPIAnalysis
from src.analysis.features import FeatureEngineering


@pytest.fixture
def sample_shipping_data():
    """Create sample shipping data for testing."""
    return pd.DataFrame({
        'rank': [1, 2, 3, 4, 5],
        'state': ['CA', 'TX', 'FL', 'NY', 'IL'],
        'postal': ['CA', 'TX', 'FL', 'NY', 'IL'],
        'population': [38802500.0, 26956958.0, 19893297.0, 19746227.0, 12880580.0],
        'population_per_rank': [38802500.0, 13478479.0, 6631099.0, 4936556.75, 2576116.0]
    })


@pytest.fixture
def sample_fuel_data():
    """Create sample fuel data for testing."""
    return pd.DataFrame({
        'state': ['CA', 'TX', 'FL', 'NY', 'IL'],
        'regular': [5.368, 3.262, 3.718, 3.521, 3.662],
        'mid_grade': [5.589, 3.763, 4.155, 4.006, 4.213],
        'premium': [5.774, 4.128, 4.475, 4.395, 4.688],
        'diesel': [6.209, 4.567, 5.074, 4.993, 4.773]
    })


class TestKPIAnalysis:
    """Test cases for KPIAnalysis class."""
    
    def test_kpi_initialization(self, sample_shipping_data, sample_fuel_data):
        """Test that KPIAnalysis initializes correctly."""
        kpi = KPIAnalysis(sample_shipping_data, sample_fuel_data)
        assert kpi.df_shipping is not None
        assert kpi.df_fuel is not None
        assert len(kpi.df_shipping) == 5
    
    def test_basic_kpis(self, sample_shipping_data):
        """Test basic KPI calculation."""
        kpi = KPIAnalysis(sample_shipping_data)
        basic_kpis = kpi.basic_kpis()
        
        assert 'total_states' in basic_kpis
        assert 'total_population' in basic_kpis
        assert 'avg_population' in basic_kpis
        
        assert basic_kpis['total_states'] == 5
        assert basic_kpis['total_population'] == sample_shipping_data['population'].sum()
        assert isinstance(basic_kpis['avg_population'], (int, float))
    
    def test_efficiency_kpis(self, sample_shipping_data):
        """Test efficiency KPI calculation."""
        kpi = KPIAnalysis(sample_shipping_data)
        eff_kpis = kpi.efficiency_kpis()
        
        assert 'avg_efficiency_score' in eff_kpis
        assert isinstance(eff_kpis['avg_efficiency_score'], (int, float))
        assert eff_kpis['avg_efficiency_score'] > 0
    
    def test_basic_kpis_returns_dict(self, sample_shipping_data):
        """Test that basic_kpis returns a dictionary."""
        kpi = KPIAnalysis(sample_shipping_data)
        result = kpi.basic_kpis()
        
        assert isinstance(result, dict)
        assert len(result) > 0
    
    def test_empty_dataframe_handling(self):
        """Test KPIAnalysis handles empty DataFrames gracefully."""
        empty_df = pd.DataFrame()
        kpi = KPIAnalysis(empty_df)
        
        # Should not raise an error
        result = kpi.basic_kpis()
        assert isinstance(result, dict)


class TestFeatureEngineering:
    """Test cases for FeatureEngineering class."""
    
    def test_feature_engineering_initialization(self, sample_shipping_data):
        """Test that FeatureEngineering initializes correctly."""
        fe = FeatureEngineering(sample_shipping_data)
        assert fe.df_shipping is not None
        assert len(fe.df_shipping) == 5
    
    def test_create_basic_features(self, sample_shipping_data):
        """Test basic feature creation."""
        fe = FeatureEngineering(sample_shipping_data)
        df_with_features = fe.create_basic_features()
        
        # Check that new columns were created
        assert 'efficiency_score' in df_with_features.columns
        assert 'log_population' in df_with_features.columns
        assert 'log_rank' in df_with_features.columns
        
        # Original columns should still exist
        assert 'rank' in df_with_features.columns
        assert 'state' in df_with_features.columns
    
    def test_create_regional_features(self, sample_shipping_data):
        """Test regional feature creation."""
        fe = FeatureEngineering(sample_shipping_data)
        df_with_features = fe.create_regional_features()
        
        # Check that region column was added
        assert 'region' in df_with_features.columns
        
        # Verify regions are assigned correctly
        regions = df_with_features['region'].unique()
        assert len(regions) > 0
        
        # Check CA is West
        ca_region = df_with_features[df_with_features['state'] == 'CA']['region'].values[0]
        assert ca_region == 'West'
    
    def test_feature_values_are_numeric(self, sample_shipping_data):
        """Test that created features are numeric."""
        fe = FeatureEngineering(sample_shipping_data)
        df_with_features = fe.create_basic_features()
        
        assert pd.api.types.is_numeric_dtype(df_with_features['efficiency_score'])
        assert pd.api.types.is_numeric_dtype(df_with_features['log_population'])
    
    def test_log_transform_valid(self, sample_shipping_data):
        """Test that log transforms produce valid (non-infinite) values."""
        fe = FeatureEngineering(sample_shipping_data)
        df_with_features = fe.create_basic_features()
        
        # Check no infinite values
        assert not np.any(np.isinf(df_with_features['log_population']))
        assert not np.any(np.isinf(df_with_features['log_rank']))
        
        # Check no NaN values
        assert not df_with_features['log_population'].isna().any()
        assert not df_with_features['log_rank'].isna().any()


class TestIntegration:
    """Integration tests combining KPI and Feature Analysis."""
    
    def test_full_analysis_pipeline(self, sample_shipping_data, sample_fuel_data):
        """Test running full analysis pipeline."""
        # Create KPI analysis
        kpi = KPIAnalysis(sample_shipping_data, sample_fuel_data)
        basic_kpis = kpi.basic_kpis()
        
        # Create feature engineering
        fe = FeatureEngineering(sample_shipping_data)
        df_enhanced = fe.create_basic_features()
        df_enhanced = fe.create_regional_features()
        
        # Verify outputs
        assert len(basic_kpis) > 0
        assert df_enhanced.shape[0] == 5
        assert df_enhanced.shape[1] > sample_shipping_data.shape[1]
    
    def test_data_consistency_after_features(self, sample_shipping_data):
        """Test that original data is not modified after feature engineering."""
        original_shape = sample_shipping_data.shape
        
        fe = FeatureEngineering(sample_shipping_data)
        df_enhanced = fe.create_basic_features()
        df_enhanced = fe.create_regional_features()
        
        # Original df should still have same shape
        assert sample_shipping_data.shape == original_shape
        
        # Enhanced df should have more columns
        assert df_enhanced.shape[1] > original_shape[1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
