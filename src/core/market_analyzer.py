"""
Advanced Market Data Analyzer

Provides comprehensive market analysis capabilities including:
- Multi-asset analysis
- Correlation analysis
- Market regime detection
- Risk metrics calculation
- Performance attribution
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from .data_loader import DataLoader
from .indicators import TechnicalIndicators, IndicatorConfig

logger = logging.getLogger(__name__)

@dataclass
class MarketRegime:
    """Market regime classification."""
    regime: str
    volatility: float
    trend_strength: float
    mean_reversion: float
    
@dataclass
class RiskMetrics:
    """Comprehensive risk metrics."""
    var_95: float
    var_99: float
    expected_shortfall: float
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    beta: float
    alpha: float

class MarketDataAnalyzer:
    """Advanced market data analysis engine."""
    
    def __init__(self, config: IndicatorConfig = None):
        self.config = config or IndicatorConfig()
        self.data_loader = DataLoader()
        self.indicators = TechnicalIndicators(self.config)
        
    def analyze_market(self, 
                      symbols: List[str], 
                      start_date: str, 
                      end_date: str,
                      benchmark: str = 'SPY') -> Dict:
        """
        Perform comprehensive market analysis.
        
        Args:
            symbols: List of symbols to analyze
            start_date: Analysis start date
            end_date: Analysis end date
            benchmark: Benchmark symbol for comparison
            
        Returns:
            Comprehensive analysis results
        """
        # Load data
        data = self.data_loader.load_data(symbols + [benchmark], start_date, end_date)
        
        # Calculate indicators for each symbol
        analysis_results = {}
        
        for symbol in symbols:
            if symbol in data and not data[symbol].empty:
                symbol_data = data[symbol].copy()
                symbol_data = self.indicators.calculate_all(symbol_data)
                
                analysis_results[symbol] = {
                    'technical_indicators': self._extract_technical_summary(symbol_data),
                    'risk_metrics': self._calculate_risk_metrics(symbol_data),
                    'market_regime': self._detect_market_regime(symbol_data),
                    'support_resistance': self.indicators.calculate_support_resistance(symbol_data),
                    'correlations': self._calculate_correlations(symbol_data, data.get(benchmark, pd.DataFrame())),
                    'performance_metrics': self._calculate_performance_metrics(symbol_data)
                }
        
        # Portfolio analysis
        if len(symbols) > 1:
            analysis_results['portfolio_analysis'] = self._analyze_portfolio(data, symbols)
        
        return analysis_results
    
    def _extract_technical_summary(self, data: pd.DataFrame) -> Dict:
        """Extract summary of technical indicators."""
        latest = data.iloc[-1]
        
        summary = {
            'current_price': latest['Close'],
            'sma_signals': {},
            'momentum_signals': {},
            'volatility_signals': {},
            'volume_signals': {}
        }
        
        # SMA signals
        for period in [20, 50, 200]:
            sma_col = f'SMA_{period}'
            if sma_col in data.columns:
                summary['sma_signals'][f'SMA_{period}'] = {
                    'value': latest[sma_col],
                    'signal': 'BUY' if latest['Close'] > latest[sma_col] else 'SELL'
                }
        
        # Momentum signals
        momentum_cols = ['RSI', 'MACD', 'Stoch_K', 'Williams_R', 'CCI']
        for col in momentum_cols:
            if col in data.columns:
                summary['momentum_signals'][col] = {
                    'value': latest[col],
                    'signal': self._interpret_momentum_indicator(col, latest[col])
                }
        
        # Volatility signals
        if 'ATR' in data.columns:
            summary['volatility_signals']['ATR'] = latest['ATR']
            summary['volatility_signals']['ATR_ratio'] = latest['ATR'] / latest['Close']
        
        # Volume signals
        if 'Volume_Ratio' in data.columns:
            summary['volume_signals']['volume_ratio'] = latest['Volume_Ratio']
            summary['volume_signals']['volume_signal'] = 'HIGH' if latest['Volume_Ratio'] > 1.5 else 'NORMAL'
        
        return summary
    
    def _interpret_momentum_indicator(self, indicator: str, value: float) -> str:
        """Interpret momentum indicator values."""
        interpretations = {
            'RSI': lambda x: 'OVERBOUGHT' if x > 70 else 'OVERSOLD' if x < 30 else 'NEUTRAL',
            'Stoch_K': lambda x: 'OVERBOUGHT' if x > 80 else 'OVERSOLD' if x < 20 else 'NEUTRAL',
            'Williams_R': lambda x: 'OVERBOUGHT' if x > -20 else 'OVERSOLD' if x < -80 else 'NEUTRAL',
            'CCI': lambda x: 'OVERBOUGHT' if x > 100 else 'OVERSOLD' if x < -100 else 'NEUTRAL'
        }
        
        return interpretations.get(indicator, lambda x: 'NEUTRAL')(value)
    
    def _calculate_risk_metrics(self, data: pd.DataFrame) -> RiskMetrics:
        """Calculate comprehensive risk metrics."""
        returns = data['Close'].pct_change().dropna()
        
        if len(returns) < 30:
            logger.warning("Insufficient data for risk calculation")
            return RiskMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        # Value at Risk
        var_95 = np.percentile(returns, 5)
        var_99 = np.percentile(returns, 1)
        
        # Expected Shortfall
        expected_shortfall = returns[returns <= var_95].mean()
        
        # Maximum Drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Sharpe Ratio
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() != 0 else 0
        
        # Sortino Ratio
        negative_returns = returns[returns < 0]
        downside_deviation = np.sqrt((negative_returns ** 2).mean()) if len(negative_returns) > 0 else 0
        sortino_ratio = returns.mean() / downside_deviation * np.sqrt(252) if downside_deviation != 0 else 0
        
        # Calmar Ratio
        calmar_ratio = returns.mean() * 252 / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Beta and Alpha (simplified calculation)
        beta = 1.0  # Placeholder - would need benchmark returns
        alpha = returns.mean() * 252  # Placeholder
        
        return RiskMetrics(
            var_95=var_95,
            var_99=var_99,
            expected_shortfall=expected_shortfall,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            beta=beta,
            alpha=alpha
        )
    
    def _detect_market_regime(self, data: pd.DataFrame) -> MarketRegime:
        """Detect current market regime."""
        returns = data['Close'].pct_change().dropna()
        
        if len(returns) < 20:
            return MarketRegime('UNKNOWN', 0, 0, 0)
        
        # Calculate volatility
        volatility = returns.rolling(window=20).std().iloc[-1] * np.sqrt(252)
        
        # Calculate trend strength using linear regression
        x = np.arange(len(returns[-20:]))
        y = data['Close'].iloc[-20:].values
        slope, _, _, _, _ = stats.linregress(x, y)
        trend_strength = abs(slope) / data['Close'].iloc[-1] * 100
        
        # Calculate mean reversion using Hurst exponent
        mean_reversion = self._calculate_hurst_exponent(returns[-100:])
        
        # Determine regime
        if volatility > 0.3:
            regime = 'HIGH_VOLATILITY'
        elif volatility < 0.1:
            regime = 'LOW_VOLATILITY'
        elif trend_strength > 0.5:
            regime = 'TRENDING'
        elif mean_reversion < 0.5:
            regime = 'MEAN_REVERTING'
        else:
            regime = 'NORMAL'
        
        return MarketRegime(regime, volatility, trend_strength, mean_reversion)
    
    def _calculate_hurst_exponent(self, returns: pd.Series) -> float:
        """Calculate Hurst exponent for mean reversion detection."""
        try:
            lags = range(2, min(100, len(returns) // 2))
            tau = [np.std(returns.rolling(window=lag).sum()) for lag in lags]
            reg = np.polyfit(np.log(lags), np.log(tau), 1)
            return reg[0]
        except:
            return 0.5
    
    def _calculate_correlations(self, data: pd.DataFrame, benchmark: pd.DataFrame) -> Dict:
        """Calculate correlation metrics."""
        if benchmark.empty or len(data) != len(benchmark):
            return {}
        
        returns = data['Close'].pct_change().dropna()
        benchmark_returns = benchmark['Close'].pct_change().dropna()
        
        # Align data
        common_dates = returns.index.intersection(benchmark_returns.index)
        if len(common_dates) < 10:
            return {}
        
        aligned_returns = returns[common_dates]
        aligned_benchmark = benchmark_returns[common_dates]
        
        correlation = aligned_returns.corr(aligned_benchmark)
        
        return {
            'correlation_with_benchmark': correlation,
            'beta': self._calculate_beta(aligned_returns, aligned_benchmark),
            'r_squared': correlation ** 2
        }
    
    def _calculate_beta(self, returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """Calculate beta against benchmark."""
        if len(returns) < 2 or benchmark_returns.std() == 0:
            return 1.0
        
        covariance = returns.cov(benchmark_returns)
        benchmark_variance = benchmark_returns.var()
        
        return covariance / benchmark_variance
    
    def _calculate_performance_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate performance metrics."""
        returns = data['Close'].pct_change().dropna()
        
        if len(returns) == 0:
            return {}
        
        total_return = (data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100
        
        # Annualized metrics
        days = len(returns)
        annualized_return = (1 + total_return / 100) ** (252 / days) - 1
        
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = annualized_return / volatility if volatility != 0 else 0
        
        return {
            'total_return_pct': total_return,
            'annualized_return_pct': annualized_return * 100,
            'volatility_pct': volatility * 100,
            'sharpe_ratio': sharpe_ratio,
            'max_consecutive_wins': self._max_consecutive_wins(returns),
            'max_consecutive_losses': self._max_consecutive_losses(returns)
        }
    
    def _max_consecutive_wins(self, returns: pd.Series) -> int:
        """Calculate maximum consecutive wins."""
        wins = (returns > 0).astype(int)
        consecutive = 0
        max_consecutive = 0
        
        for win in wins:
            if win == 1:
                consecutive += 1
                max_consecutive = max(max_consecutive, consecutive)
            else:
                consecutive = 0
        
        return max_consecutive
    
    def _max_consecutive_losses(self, returns: pd.Series) -> int:
        """Calculate maximum consecutive losses."""
        losses = (returns < 0).astype(int)
        consecutive = 0
        max_consecutive = 0
        
        for loss in losses:
            if loss == 1:
                consecutive += 1
                max_consecutive = max(max_consecutive, consecutive)
            else:
                consecutive = 0
        
        return max_consecutive
    
    def _analyze_portfolio(self, data: Dict[str, pd.DataFrame], symbols: List[str]) -> Dict:
        """Analyze portfolio-level metrics."""
        returns_data = {}
        
        for symbol in symbols:
            if symbol in data and not data[symbol].empty:
                returns_data[symbol] = data[symbol]['Close'].pct_change()
        
        if not returns_data:
            return {}
        
        # Create returns DataFrame
        returns_df = pd.DataFrame(returns_data).dropna()
        
        # Correlation matrix
        correlation_matrix = returns_df.corr()
        
        # PCA analysis
        pca = PCA(n_components=min(3, len(symbols)))
        returns_scaled = StandardScaler().fit_transform(returns_df)
        pca_results = pca.fit_transform(returns_scaled)
        
        # Portfolio optimization (equal weights)
        n_assets = len(symbols)
        weights = np.ones(n_assets) / n_assets
        
        portfolio_returns = (returns_df * weights).sum(axis=1)
        
        return {
            'correlation_matrix': correlation_matrix.to_dict(),
            'pca_explained_variance': pca.explained_variance_ratio_.tolist(),
            'portfolio_volatility': portfolio_returns.std() * np.sqrt(252),
            'diversification_ratio': self._calculate_diversification_ratio(correlation_matrix)
        }
    
    def _calculate_diversification_ratio(self, correlation_matrix: pd.DataFrame) -> float:
        """Calculate portfolio diversification ratio."""
        n_assets = len(correlation_matrix)
        if n_assets == 1:
            return 1.0
        
        # Average correlation
        avg_corr = correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean()
        
        return 1 / (avg_corr * np.sqrt(n_assets))
