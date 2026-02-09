import pytest
from src.etl.scrapers.fuel_scraper import scrape_fuel_prices

def test_fuel_scraper_returns_data():
    """Test that fuel scraper returns non-empty DataFrame"""
    df = scrape_fuel_prices()
    assert df is not None
    assert len(df) > 0
    assert 'state' in df.columns
    assert 'regular' in df.columns
