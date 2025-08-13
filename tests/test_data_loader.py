"""Tests for the data loader module."""

import pytest
import pandas as pd
from datetime import datetime, timedelta
import tempfile
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.data_loader import DataLoader, YahooFinanceSource, AlphaVantageSource

class TestDataLoader:
    """Test suite for data loader functionality."""
    
    def test_yahoo_finance_source(self):
        """Test Yahoo Finance data source."""
        source = YahooFinanceSource()
        
        # Test with valid symbol
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        data = source.fetch_data('AAPL', start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        
        assert isinstance(data, pd.DataFrame)
        assert not data.empty
        assert all(col in data.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])
        
    def test_yahoo_finance_invalid_symbol(self):
        """Test Yahoo Finance with invalid symbol."""
        source = YahooFinanceSource()
        
        with pytest.raises(ValueError):
            source.fetch_data('INVALID_SYMBOL_XYZ', '2023-01-01', '2023-12-31')
    
    def test_data_loader_initialization(self):
        """Test DataLoader initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = DataLoader(cache_dir=temp_dir)
            assert loader.cache_dir == temp_dir
            assert os.path.exists(temp_dir)
    
    def test_data_loader_single_symbol(self):
        """Test loading data for single symbol."""
        loader = DataLoader()
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        results = loader.load_data(
            ['AAPL'], 
            start_date.strftime('%Y-%m-%d'), 
            end_date.strftime('%Y-%m-%d')
        )
        
        assert 'AAPL' in results
        assert isinstance(results['AAPL'], pd.DataFrame)
        assert not results['AAPL'].empty
    
    def test_data_loader_multiple_symbols(self):
        """Test loading data for multiple symbols."""
        loader = DataLoader()
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        results = loader.load_data(
            symbols, 
            start_date.strftime('%Y-%m-%d'), 
            end_date.strftime('%Y-%m-%d')
        )
        
        for symbol in symbols:
            assert symbol in results
            assert isinstance(results[symbol], pd.DataFrame)
    
    def test_data_validation(self):
        """Test data validation functionality."""
        loader = DataLoader()
        
        # Test with empty DataFrame
        empty_df = pd.DataFrame()
        with pytest.raises(ValueError):
            loader._validate_data(empty_df)
        
        # Test with missing columns
        invalid_df = pd.DataFrame({'Open': [1, 2, 3]})
        with pytest.raises(ValueError):
            loader._validate_data(invalid_df)
    
    def test_real_time_data(self):
        """Test real-time data fetching."""
        loader = DataLoader()
        
        results = loader.get_real_time_data(['AAPL', 'GOOGL'])
        
        assert isinstance(results, dict)
        assert 'AAPL' in results
        assert 'GOOGL' in results
        
        # Check structure
        for symbol, data in results.items():
            if data is not None:
                assert 'current_price' in data
                assert 'volume' in data
                assert 'market_cap' in data
    
    def test_caching_functionality(self):
        """Test data caching."""
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = DataLoader(cache_dir=temp_dir)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            # First load (should cache)
            results1 = loader.load_data(
                ['AAPL'], 
                start_date.strftime('%Y-%m-%d'), 
                end_date.strftime('%Y-%m-%d'),
                use_cache=True
            )
            
            # Second load (should use cache)
            results2 = loader.load_data(
                ['AAPL'], 
                start_date.strftime('%Y-%m-%d'), 
                end_date.strftime('%Y-%m-%d'),
                use_cache=True
            )
            
            assert not results1['AAPL'].empty
            assert not results2['AAPL'].empty
            assert len(results1['AAPL']) == len(results2['AAPL'])

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
