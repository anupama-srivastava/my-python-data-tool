"""
Advanced Python Data Analysis Tool for Market Data Analysis

A professional-grade, enterprise-level Python toolkit for comprehensive
financial data analysis, backtesting, and visualization.

Features:
- Real-time data acquisition from multiple sources
- Advanced technical indicators and machine learning models
- Professional backtesting engine with risk management
- Interactive dashboards and reporting
- Portfolio optimization and performance analytics
- Event-driven architecture for live trading
"""

__version__ = "2.0.0"
__author__ = "Advanced Data Analytics Team"
__email__ = "analytics@company.com"

from .core import MarketDataAnalyzer
from .backtest import BacktestEngine
from .portfolio import PortfolioManager
from .visualization import Dashboard

__all__ = [
    "MarketDataAnalyzer",
    "BacktestEngine", 
    "PortfolioManager",
    "Dashboard"
]
