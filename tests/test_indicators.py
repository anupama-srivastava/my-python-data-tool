"""Tests for the technical indicators module."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.indicators import TechnicalIndicators, IndicatorConfig

@pytest.fixture
def sample_data():
    """Generate sample OHLCV data for testing."""
    dates = pd.date_range(end=datetime.now(), periods=100)
    data = pd.DataFrame({
        'Open': np.random.uniform(100, 200, size=100),
        'High': np.random.uniform(100, 200, size=100),
        'Low': np.random.uniform(100, 200, size=100),
        'Close': np.random.uniform(100, 200, size=100),
        'Volume': np.random.randint(1000, 10000, size=100)
    }, index=dates)
    return data

def test_calculate_all_indicators(sample_data):
    """Test calculation of all technical indicators."""
    indicators = TechnicalIndicators()
    result = indicators.calculate_all(sample_data)
    
    # Check that key columns exist
    expected_columns = [
        'SMA_5', 'SMA_10', 'SMA_20', 'SMA_50', 'SMA_200',
        'EMA_8', 'EMA_12', 'EMA_21', 'EMA_26', 'EMA_50',
        'RSI', 'MACD', 'MACD_Signal', 'MACD_Histogram',
        'BB_Upper', 'BB_Lower', 'BB_Middle', 'BB_Width', 'BB_Position',
        'Stoch_K', 'Stoch_D', 'Williams_R', 'CCI', 'OBV', 'Volume_ROC',
        'ATR', 'KC_Upper', 'KC_Lower', 'Ichimoku_Tenkan', 'VWAP'
    ]
    
    for col in expected_columns:
        assert col in result.columns, f"Missing indicator column: {col}"
    
    # Check that no NaN values in key indicators after initial periods
    assert not result['SMA_20'].iloc[19:].isnull().any()
    assert not result['RSI'].iloc[13:].isnull().any()
    assert not result['MACD'].iloc[25:].isnull().any()

def test_signal_summary(sample_data):
    """Test signal summary generation."""
    indicators = TechnicalIndicators()
    df = indicators.calculate_all(sample_data)
    summary = indicators.get_signal_summary(df)
    
    assert isinstance(summary, dict)
    # Signals keys should be present
    assert any('Signal' in key or 'Cross' in key for key in summary.keys())

def test_support_resistance(sample_data):
    """Test support and resistance calculation."""
    indicators = TechnicalIndicators()
    df = indicators.calculate_all(sample_data)
    levels = indicators.calculate_support_resistance(df)
    
    assert 'support' in levels and 'resistance' in levels
    assert isinstance(levels['support'], list)
    assert isinstance(levels['resistance'], list)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
