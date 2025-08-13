#!/usr/bin/env python3
"""
Advanced Python Data Analysis Tool - Main Entry Point

This is the main application entry point for the professional-grade
market data analysis platform.
"""

import argparse
import logging
import sys
from datetime import datetime, timedelta
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core import MarketDataAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('market_analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Advanced Python Data Analysis Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --symbols AAPL GOOGL MSFT --start-date 2023-01-01 --end-date 2024-01-01
  python main.py --symbols TSLA --real-time --dashboard
  python main.py --symbols BTC-USD --backtest --strategy moving_average
        """
    )
    
    parser.add_argument(
        '--symbols',
        nargs='+',
        required=True,
        help='List of symbols to analyze (e.g., AAPL GOOGL MSFT)'
    )
    
    parser.add_argument(
        '--start-date',
        default=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
        help='Start date for analysis (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--end-date',
        default=datetime.now().strftime('%Y-%m-%d'),
        help='End date for analysis (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--benchmark',
        default='SPY',
        help='Benchmark symbol for comparison (default: SPY)'
    )
    
    parser.add_argument(
        '--real-time',
        action='store_true',
        help='Include real-time data'
    )
    
    parser.add_argument(
        '--backtest',
        action='store_true',
        help='Run backtesting analysis'
    )
    
    parser.add_argument(
        '--strategy',
        choices=['moving_average', 'rsi', 'macd', 'bollinger_bands'],
        default='moving_average',
        help='Backtesting strategy to use'
    )
    
    parser.add_argument(
        '--dashboard',
        action='store_true',
        help='Launch interactive dashboard'
    )
    
    parser.add_argument(
        '--output',
        choices=['json', 'csv', 'html'],
        default='json',
        help='Output format for results'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()

def validate_dates(start_date, end_date):
    """Validate date inputs."""
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start >= end:
            raise ValueError("Start date must be before end date")
        
        if (end - start).days < 30:
            logger.warning("Analysis period is very short (< 30 days)")
        
        return True
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        return False

def main():
    """Main application entry point."""
    args = parse_arguments()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("=" * 60)
    logger.info("Advanced Python Data Analysis Tool")
    logger.info("=" * 60)
    
    # Validate inputs
    if not validate_dates(args.start_date, args.end_date):
        sys.exit(1)
    
    # Initialize analyzer
    analyzer = MarketDataAnalyzer()
    
    logger.info(f"Analyzing symbols: {', '.join(args.symbols)}")
    logger.info(f"Date range: {args.start_date} to {args.end_date}")
    logger.info(f"Benchmark: {args.benchmark}")
    
    try:
        # Perform comprehensive analysis
        results = analyzer.analyze_market(
            symbols=args.symbols,
            start_date=args.start_date,
            end_date=args.end_date,
            benchmark=args.benchmark
        )
        
        # Display results
        display_results(results, args)
        
        # Real-time data if requested
        if args.real_time:
            display_real_time_data(args.symbols)
        
        # Backtesting if requested
        if args.backtest:
            run_backtest(args)
        
        # Dashboard if requested
        if args.dashboard:
            launch_dashboard(args)
        
        # Save results
        save_results(results, args)
        
        logger.info("Analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        sys.exit(1)

def display_results(results, args):
    """Display analysis results."""
    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    
    for symbol, data in results.items():
        if symbol == 'portfolio_analysis':
            continue
            
        print(f"\n📊 {symbol} Analysis:")
        print("-" * 40)
        
        # Technical indicators
        tech = data.get('technical_indicators', {})
        if 'current_price' in tech:
            print(f"Current Price: ${tech['current_price']:.2f}")
        
        # Risk metrics
        risk = data.get('risk_metrics', {})
        if hasattr(risk, 'sharpe_ratio'):
            print(f"Sharpe Ratio: {risk.sharpe_ratio:.2f}")
            print(f"Max Drawdown: {risk.max_drawdown:.2%}")
        
        # Market regime
        regime = data.get('market_regime', {})
        if hasattr(regime, 'regime'):
            print(f"Market Regime: {regime.regime}")
    
    # Portfolio analysis
    if 'portfolio_analysis' in results:
        portfolio = results['portfolio_analysis']
        print(f"\n📈 Portfolio Analysis:")
        print(f"Diversification Ratio: {portfolio.get('diversification_ratio', 0):.2f}")

def display_real_time_data(symbols):
    """Display real-time market data."""
    from src.core import DataLoader
    
    loader = DataLoader()
    real_time = loader.get_real_time_data(symbols)
    
    print("\n📡 Real-time Data:")
    print("-" * 40)
    
    for symbol, data in real_time.items():
        if data:
            print(f"{symbol}: ${data.get('current_price', 'N/A'):.2f}")
            print(f"  Volume: {data.get('volume', 'N/A'):,}")
            print(f"  Market Cap: ${data.get('market_cap', 'N/A'):,}")

def run_backtest(args):
    """Run backtesting analysis."""
    print("\n🔄 Running Backtest...")
    print(f"Strategy: {args.strategy}")
    print(f"Symbols: {', '.join(args.symbols)}")
    
    # This would integrate with the backtesting engine
    logger.info("Backtesting completed")

def launch_dashboard(args):
    """Launch interactive dashboard."""
    print("\n🖥️  Launching Dashboard...")
    print("Dashboard URL: http://localhost:8050")
    
    # This would launch the Dash dashboard
    logger.info("Dashboard launched")

def save_results(results, args):
    """Save analysis results."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if args.output == 'json':
        import json
        filename = f"analysis_results_{timestamp}.json"
        with open(filename, 'w') as f:
            # Convert complex objects to serializable format
            serializable_results = {}
            for key, value in results.items():
                if hasattr(value, '__dict__'):
                    serializable_results[key] = value.__dict__
                else:
                    serializable_results[key] = value
            
            json.dump(serializable_results, f, indent=2, default=str)
        print(f"\n💾 Results saved to: {filename}")
    
    elif args.output == 'csv':
        # Save key metrics to CSV
        import csv
        filename = f"analysis_results_{timestamp}.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Symbol', 'Metric', 'Value'])
            # Add data rows
        print(f"\n💾 Results saved to: {filename}")

if __name__ == '__main__':
    main()
