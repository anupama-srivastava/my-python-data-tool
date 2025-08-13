"""
Advanced Technical Indicators Module

Provides comprehensive technical analysis capabilities including:
- Traditional indicators (SMA, EMA, RSI, MACD, Bollinger Bands)
- Advanced indicators (Ichimoku, Keltner Channels, ATR)
- Volume indicators (OBV, VWAP, Volume Profile)
- Momentum indicators (Stochastic, Williams %R, CCI)
- Custom indicator creation framework
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class IndicatorConfig:
    """Configuration for technical indicators."""
    sma_periods: List[int] = None
    ema_periods: List[int] = None
    rsi_period: int = 14
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    bb_period: int = 20
    bb_std: float = 2.0
    stochastic_k: int = 14
    stochastic_d: int = 3
    
    def __post_init__(self):
        if self.sma_periods is None:
            self.sma_periods = [5, 10, 20, 50, 200]
        if self.ema_periods is None:
            self.ema_periods = [8, 12, 21, 26, 50]

class TechnicalIndicators:
    """Comprehensive technical analysis toolkit."""
    
    def __init__(self, config: IndicatorConfig = None):
        self.config = config or IndicatorConfig()
    
    def calculate_all(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate all available technical indicators."""
        df = data.copy()
        
        # Price-based indicators
        df = self._calculate_moving_averages(df)
        df = self._calculate_rsi(df)
        df = self._calculate_macd(df)
        df = self._calculate_bollinger_bands(df)
        df = self._calculate_stochastic(df)
        df = self._calculate_williams_r(df)
        df = self._calculate_cci(df)
        
        # Volume-based indicators
        df = self._calculate_volume_indicators(df)
        
        # Volatility indicators
        df = self._calculate_atr(df)
        df = self._calculate_keltner_channels(df)
        
        # Advanced indicators
        df = self._calculate_ichimoku(df)
        df = self._calculate_vwap(df)
        
        return df
    
    def _calculate_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate various moving averages."""
        for period in self.config.sma_periods:
            df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean()
        
        for period in self.config.ema_periods:
            df[f'EMA_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()
        
        # Golden/Death Cross
        if 'SMA_50' in df.columns and 'SMA_200' in df.columns:
            df['Golden_Cross'] = ((df['SMA_50'] > df['SMA_200']) & 
                                 (df['SMA_50'].shift(1) <= df['SMA_200'].shift(1))).astype(int)
            df['Death_Cross'] = ((df['SMA_50'] < df['SMA_200']) & 
                                (df['SMA_50'].shift(1) >= df['SMA_200'].shift(1))).astype(int)
        
        return df
    
    def _calculate_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Relative Strength Index."""
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.config.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.config.rsi_period).mean()
        
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # RSI-based signals
        df['RSI_Overbought'] = (df['RSI'] > 70).astype(int)
        df['RSI_Oversold'] = (df['RSI'] < 30).astype(int)
        
        return df
    
    def _calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD and related indicators."""
        ema_fast = df['Close'].ewm(span=self.config.macd_fast, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=self.config.macd_slow, adjust=False).mean()
        
        df['MACD'] = ema_fast - ema_slow
        df['MACD_Signal'] = df['MACD'].ewm(span=self.config.macd_signal, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # MACD signals
        df['MACD_Bullish_Cross'] = ((df['MACD'] > df['MACD_Signal']) & 
                                   (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1))).astype(int)
        df['MACD_Bearish_Cross'] = ((df['MACD'] < df['MACD_Signal']) & 
                                   (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1))).astype(int)
        
        return df
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands and related metrics."""
        sma = df['Close'].rolling(window=self.config.bb_period).mean()
        std = df['Close'].rolling(window=self.config.bb_period).std()
        
        df['BB_Upper'] = sma + (std * self.config.bb_std)
        df['BB_Lower'] = sma - (std * self.config.bb_std)
        df['BB_Middle'] = sma
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        # Bollinger Band signals
        df['BB_Overbought'] = (df['Close'] > df['BB_Upper']).astype(int)
        df['BB_Oversold'] = (df['Close'] < df['BB_Lower']).astype(int)
        
        return df
    
    def _calculate_stochastic(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Stochastic Oscillator."""
        low_min = df['Low'].rolling(window=self.config.stochastic_k).min()
        high_max = df['High'].rolling(window=self.config.stochastic_k).max()
        
        df['Stoch_K'] = 100 * ((df['Close'] - low_min) / (high_max - low_min))
        df['Stoch_D'] = df['Stoch_K'].rolling(window=self.config.stochastic_d).mean()
        
        # Stochastic signals
        df['Stoch_Overbought'] = (df['Stoch_K'] > 80).astype(int)
        df['Stoch_Oversold'] = (df['Stoch_K'] < 20).astype(int)
        
        return df
    
    def _calculate_williams_r(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Williams %R."""
        high_max = df['High'].rolling(window=14).max()
        low_min = df['Low'].rolling(window=14).min()
        
        df['Williams_R'] = -100 * ((high_max - df['Close']) / (high_max - low_min))
        
        return df
    
    def _calculate_cci(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Commodity Channel Index."""
        tp = (df['High'] + df['Low'] + df['Close']) / 3
        sma_tp = tp.rolling(window=20).mean()
        mad = tp.rolling(window=20).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
        
        df['CCI'] = (tp - sma_tp) / (0.015 * mad)
        
        return df
    
    def _calculate_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate volume-based indicators."""
        # On-Balance Volume (OBV)
        df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
        
        # Volume Rate of Change
        df['Volume_ROC'] = df['Volume'].pct_change(periods=10) * 100
        
        # Volume Moving Average
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
        
        return df
    
    def _calculate_atr(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Average True Range."""
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        
        df['ATR'] = true_range.rolling(window=14).mean()
        
        return df
    
    def _calculate_keltner_channels(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Keltner Channels."""
        ema = df['Close'].ewm(span=20, adjust=False).mean()
        atr = df['ATR'] if 'ATR' in df.columns else self._calculate_atr(df)['ATR']
        
        df['KC_Upper'] = ema + (atr * 2)
        df['KC_Lower'] = ema - (atr * 2)
        df['KC_Middle'] = ema
        
        return df
    
    def _calculate_ichimoku(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Ichimoku Cloud indicators."""
        # Tenkan-sen (Conversion Line)
        period9_high = df['High'].rolling(window=9).max()
        period9_low = df['Low'].rolling(window=9).min()
        df['Ichimoku_Tenkan'] = (period9_high + period9_low) / 2
        
        # Kijun-sen (Base Line)
        period26_high = df['High'].rolling(window=26).max()
        period26_low = df['Low'].rolling(window=26).min()
        df['Ichimoku_Kijun'] = (period26_high + period26_low) / 2
        
        # Senkou Span A (Leading Span A)
        df['Ichimoku_Senkou_A'] = ((df['Ichimoku_Tenkan'] + df['Ichimoku_Kijun']) / 2).shift(26)
        
        # Senkou Span B (Leading Span B)
        period52_high = df['High'].rolling(window=52).max()
        period52_low = df['Low'].rolling(window=52).min()
        df['Ichimoku_Senkou_B'] = ((period52_high + period52_low) / 2).shift(26)
        
        # Chikou Span (Lagging Span)
        df['Ichimoku_Chikou'] = df['Close'].shift(-26)
        
        return df
    
    def _calculate_vwap(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Volume Weighted Average Price."""
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        cumulative_tpv = (typical_price * df['Volume']).cumsum()
        cumulative_volume = df['Volume'].cumsum()
        
        df['VWAP'] = cumulative_tpv / cumulative_volume
        
        return df
    
    def get_signal_summary(self, df: pd.DataFrame) -> Dict[str, int]:
        """Generate a summary of all technical signals."""
        signal_columns = [col for col in df.columns if 'Signal' in col or 'Cross' in col or 'Overbought' in col or 'Oversold' in col]
        
        summary = {}
        for col in signal_columns:
            if col in df.columns:
                summary[col] = int(df[col].iloc[-1]) if not df[col].empty else 0
        
        return summary
    
    def calculate_support_resistance(self, df: pd.DataFrame, window: int = 20) -> Dict[str, List[float]]:
        """Calculate support and resistance levels."""
        highs = df['High'].rolling(window=window, center=True).max()
        lows = df['Low'].rolling(window=window, center=True).min()
        
        # Find local maxima and minima
        resistance_levels = highs[highs == highs.rolling(window=window, center=True).max()].dropna()
        support_levels = lows[lows == lows.rolling(window=window, center=True).min()].dropna()
        
        # Get top 3 levels
        top_resistance = resistance_levels.nlargest(3).tolist()
        top_support = support_levels.nsmallest(3).tolist()
        
        return {
            'resistance': top_resistance,
            'support': top_support
        }
