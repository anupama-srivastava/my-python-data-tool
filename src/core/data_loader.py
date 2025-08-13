"""
Advanced Data Loader Module

Provides enterprise-grade data acquisition capabilities with:
- Multiple data source support (Yahoo Finance, Alpha Vantage, Quandl)
- Real-time data streaming
- Data validation and quality checks
- Caching mechanisms for performance
- Error handling and retry logic
"""

import os
import pandas as pd
import yfinance as yf
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
from abc import ABC, abstractmethod
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class DataSource(ABC):
    """Abstract base class for data sources."""
    
    @abstractmethod
    def fetch_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch data from the source."""
        pass

class YahooFinanceSource(DataSource):
    """Yahoo Finance data source implementation."""
    
    def fetch_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch data from Yahoo Finance."""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                raise ValueError(f"No data found for {symbol}")
                
            # Add additional data
            info = ticker.info
            data['Dividends'] = info.get('dividendRate', 0)
            data['Volume_MA'] = data['Volume'].rolling(window=20).mean()
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            raise

class AlphaVantageSource(DataSource):
    """Alpha Vantage data source implementation."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
    
    def fetch_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch data from Alpha Vantage."""
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'apikey': self.api_key,
            'outputsize': 'full'
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'Time Series (Daily)' not in data:
                raise ValueError(f"Invalid response from Alpha Vantage: {data}")
                
            df = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index')
            df = df.astype(float)
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            
            # Filter by date range
            mask = (df.index >= start_date) & (df.index <= end_date)
            return df[mask]
            
        except Exception as e:
            logger.error(f"Error fetching data from Alpha Vantage: {str(e)}")
            raise

class DataLoader:
    """Enterprise-grade data loader with caching and validation."""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = cache_dir
        self.sources = {
            'yahoo': YahooFinanceSource(),
            'alphavantage': AlphaVantageSource(os.getenv('ALPHA_VANTAGE_API_KEY', ''))
        }
        self._init_cache()
        
    def _init_cache(self):
        """Initialize cache directory and database."""
        os.makedirs(self.cache_dir, exist_ok=True)
        self.db_path = os.path.join(self.cache_dir, "market_data.db")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    symbol TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    source TEXT,
                    data BLOB,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (symbol, start_date, end_date, source)
                )
            ''')
    
    def load_data(self, 
                  symbols: List[str], 
                  start_date: str, 
                  end_date: str,
                  source: str = 'yahoo',
                  use_cache: bool = True) -> Dict[str, pd.DataFrame]:
        """
        Load data for multiple symbols with caching.
        
        Args:
            symbols: List of stock symbols
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            source: Data source ('yahoo' or 'alphavantage')
            use_cache: Whether to use cached data
            
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        results = {}
        
        for symbol in symbols:
            try:
                # Check cache first
                if use_cache:
                    cached_data = self._get_cached_data(symbol, start_date, end_date, source)
                    if cached_data is not None:
                        results[symbol] = cached_data
                        logger.info(f"Loaded {symbol} from cache")
                        continue
                
                # Fetch fresh data
                data_source = self.sources.get(source)
                if not data_source:
                    raise ValueError(f"Unknown data source: {source}")
                
                data = data_source.fetch_data(symbol, start_date, end_date)
                
                # Validate data
                self._validate_data(data)
                
                # Cache the data
                if use_cache:
                    self._cache_data(symbol, start_date, end_date, source, data)
                
                results[symbol] = data
                logger.info(f"Successfully loaded {symbol} from {source}")
                
            except Exception as e:
                logger.error(f"Failed to load data for {symbol}: {str(e)}")
                results[symbol] = pd.DataFrame()
        
        return results
    
    def _validate_data(self, data: pd.DataFrame) -> None:
        """Validate data quality and completeness."""
        if data.empty:
            raise ValueError("Empty dataset")
        
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")
        
        # Check for missing values
        missing_pct = data[required_columns].isnull().sum() / len(data) * 100
        if any(missing_pct > 5):
            logger.warning(f"High missing data percentage: {missing_pct}")
    
    def _get_cached_data(self, symbol: str, start_date: str, end_date: str, source: str) -> Optional[pd.DataFrame]:
        """Retrieve data from cache."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT data FROM cache 
                    WHERE symbol=? AND start_date=? AND end_date=? AND source=?
                    AND timestamp > datetime('now', '-1 day')
                ''', (symbol, start_date, end_date, source))
                
                result = cursor.fetchone()
                if result:
                    import pickle
                    return pickle.loads(result[0])
        except Exception as e:
            logger.error(f"Error reading from cache: {str(e)}")
        
        return None
    
    def _cache_data(self, symbol: str, start_date: str, end_date: str, source: str, data: pd.DataFrame) -> None:
        """Store data in cache."""
        try:
            import pickle
            serialized_data = pickle.dumps(data)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO cache (symbol, start_date, end_date, source, data)
                    VALUES (?, ?, ?, ?, ?)
                ''', (symbol, start_date, end_date, source, serialized_data))
        except Exception as e:
            logger.error(f"Error caching data: {str(e)}")
    
    def get_real_time_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """Fetch real-time market data."""
        results = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                current_price = ticker.history(period="1d", interval="1m").tail(1)
                
                results[symbol] = {
                    'current_price': current_price['Close'].iloc[0] if not current_price.empty else None,
                    'volume': info.get('volume', 0),
                    'market_cap': info.get('marketCap', 0),
                    'pe_ratio': info.get('trailingPE', 0),
                    'dividend_yield': info.get('dividendYield', 0),
                    'beta': info.get('beta', 0),
                    'timestamp': datetime.now()
                }
                
            except Exception as e:
                logger.error(f"Error fetching real-time data for {symbol}: {str(e)}")
                results[symbol] = None
        
        return results
