"""Tests for the market analyzer module."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.market_analyzer import MarketDataAnalyzer, RiskMetrics, MarketRegime

class TestMarketAnalyzer:
    """Test suite for market analyzer functionality."""
    
    def test_analyzer_initialization(self):
        """Test MarketDataAnalyzer initialization."""
        analyzer = MarketDataAnalyzer()
        assert analyzer is not None
    
    def test_risk_metrics_calculation(self):
        """Test risk metrics calculation."""
        analyzer = MarketDataAnalyzer()
        
        # Create sample data
        dates = pd.date_range(end=datetime.now(), periods=100)
        data = pd.DataFrame({
            'Open': np.random.uniform(100, 200, size=100),
            'High': np.random.uniform(100, 200, size=100),
            'Low': np.random.uniform(100, 200, size=100),
            'Close': np.linspace(100, 150, 100),  # Trending data
            'Volume': np.random.randint(1000, 10000, size=100)
        }, index=dates)
        
        risk_metrics = analyzer._calculate_risk_metrics(data)
        
        assert isinstance(risk_metrics, RiskMetrics)
        assert isinstance(risk_metrics.sharpe_ratio, (int, float))
        assert isinstance(risk_metrics.max_drawdown, (int, float))
        assert isinstance(risk_metrics.var_95, (int, float))
    
    def test_market_regime_detection(self):
        """Test market regime detection."""
        analyzer = MarketDataAnalyzer()
        
        # Create trending data
        dates = pd.date_range(end=datetime.now(), periods=100)
        data = pd.DataFrame({
            'Open': np.linspace(100, 150, 100),
            'High': np.linspace(101, 151, 100),
            'Low': np.linspace(99, 149, 100),
            'Close': np.linspace(100, 150, 100),
            'Volume': np.random.randint(1000, 10000, size=100)
        }, index=dates)
        
        regime = analyzer._detect_market_regime(data)
        
        assert isinstance(regime, MarketRegime)
        assert isinstance(regime.regime, str)
        assert regime.regime in ['TRENDING', 'NORMAL', 'HIGH_VOLATILITY', 'LOW_VOLATILITY', 'MEAN_REVERTING', 'UNKNOWN']
    
    def test_performance_metrics(self):
        """Test performance metrics calculation."""
        analyzer = MarketDataAnalyzer()
        
        # Create sample data with known return
        dates = pd.date_range(end=datetime.now(), periods=100)
        data = pd.DataFrame({
            'Open': [100] * 100,
            'High': [110] * 100,
            'Low': [90] * 100,
            'Close': np.linspace(100, 110, 100),  # 10% return
            'Volume': [1000] * 100
        }, index=dates)
        
        metrics = analyzer._calculate_performance_metrics(data)
        
        assert isinstance(metrics, dict)
        assert 'total_return_pct' in metrics
        assert metrics['total_return_pct'] > 0
    
    def test_correlation_calculation(self):
        """Test correlation calculation."""
        analyzer = MarketDataAnalyzer()
        
        # Create correlated data
        dates = pd.date_range(end=datetime.now(), periods=100)
        base_returns = np.random.normal(0, 0.01, 100)
        
        data1 = pd.DataFrame({
            'Open': [100] * 100,
            'High': [110] * 100,
            'Low': [90] * 100,
            'Close': 100 * (1 + base_returns).cumprod(),
            'Volume': [1000] * 100
        }, index=dates)
        
        data2 = pd.DataFrame({
            'Open': [100] * 100,
            'High': [110] * 100,
            'Low': [90] * 100,
            'Close': 100 * (1 + base_returns * 0.8).cumprod(),  # 80% correlation
            'Volume': [1000] * 100
        }, index=dates)
        
        correlations = analyzer._calculate_correlations(data1, data2)
        
        assert isinstance(correlations, dict)
        if correlations:  # Only check if data is valid
            assert 'correlation_with_benchmark' in correlations
            assert abs(correlations['correlation_with_benchmark'] - 0.8) < 0.2
    
    def test_portfolio_analysis(self):
        """Test portfolio analysis."""
        analyzer = MarketDataAnalyzer()
        
        # Create sample portfolio data
        dates = pd.date_range(end=datetime.now(), periods=100)
        data = {
            'AAPL': pd.DataFrame({
                'Open': [100] * 100,
                'High': [110] * 100,
                'Low': [90] * 100,
                'Close': np.random.uniform(100, 200, 100),
                'Volume': [1000] * 100
            }, index=dates),
            'GOOGL': pd.DataFrame({
                'Open': [200] * 100,
                'High': [220] * 100,
                'Low': [180] * 100,
                'Close': np.random.uniform(200, 400, 100),
                'Volume': [2000] * 100
            }, index=dates)
        }
        
        portfolio_analysis = analyzer._analyze_portfolio(data, ['AAPL', 'GOOGL'])
        
        assert isinstance(portfolio_analysis, dict)
        assert 'correlation_matrix' in portfolio_analysis
        assert 'diversification_ratio' in portfolio_analysis
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        analyzer = MarketDataAnalyzer()
        
        # Test with empty DataFrame
        empty_data = pd.DataFrame()
        risk_metrics = analyzer._calculate_risk_metrics(empty_data)
        assert risk_metrics.sharpe_ratio == 0
        
        # Test with insufficient data
        dates = pd.date_range(end=datetime.now(), periods=5)
        short_data = pd.DataFrame({
            'Open': [100] * 5,
            'High': [110] * 5,
            'Low': [90] * 5,
            'Close': [100] * 5,
            'Volume': [1000] * 5
        }, index=dates)
        
        regime = analyzer._detect_market_regime(short_data)
        assert regime.regime == 'UNKNOWN'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
