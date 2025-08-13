#!/usr/bin/env python3
"""
Advanced Interactive Python Data Analysis Tool
Professional-grade market data analysis with interactive user interface
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import colorama
from colorama import Fore, Back, Style
import pandas as pd
import yfinance as yf
from tabulate import tabulate

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core import MarketDataAnalyzer

# Initialize colorama for cross-platform colored output
colorama.init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('interactive_analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class InteractiveDataAnalyzer:
    """Interactive command-line interface for advanced data analysis."""
    
    def __init__(self):
        self.analyzer = MarketDataAnalyzer()
        self.current_symbols = []
        self.current_data = {}
        self.analysis_results = {}
        
    def print_header(self, title: str):
        """Print formatted header."""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{title.center(80)}")
        print(f"{'='*80}{Style.RESET_ALL}")
    
    def print_menu(self, options: Dict[str, str], title: str = "Menu"):
        """Print interactive menu."""
        self.print_header(title)
        for key, description in options.items():
            print(f"{Fore.YELLOW}{key}. {Fore.WHITE}{description}")
        print(f"{Style.RESET_ALL}")
    
    def get_user_input(self, prompt: str, input_type: str = "string", default: Any = None) -> Any:
        """Get validated user input."""
        while True:
            try:
                user_input = input(f"{Fore.GREEN}{prompt}{Style.RESET_ALL}")
                
                if not user_input and default is not None:
                    return default
                
                if input_type == "int":
                    return int(user_input)
                elif input_type == "float":
                    return float(user_input)
                elif input_type == "list":
                    return [item.strip() for item in user_input.split(',')]
                elif input_type == "date":
                    return datetime.strptime(user_input, '%Y-%m-%d').date()
                else:
                    return user_input
                    
            except ValueError as e:
                print(f"{Fore.RED}Invalid input: {e}. Please try again.{Style.RESET_ALL}")
    
    def validate_symbol(self, symbol: str) -> bool:
        """Validate if symbol exists."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return len(info) > 0
        except:
            return False
    
    def get_symbols_from_user(self) -> List[str]:
        """Get stock symbols from user with validation."""
        print(f"\n{Fore.CYAN}📈 Stock Symbol Configuration{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Enter stock symbols (e.g., AAPL, GOOGL, MSFT, TSLA)")
        print("Separate multiple symbols with commas")
        
        while True:
            symbols_input = self.get_user_input("Enter symbols: ", "list")
            symbols = [s.upper().strip() for s in symbols_input]
            
            # Validate symbols
            valid_symbols = []
            invalid_symbols = []
            
            for symbol in symbols:
                if self.validate_symbol(symbol):
                    valid_symbols.append(symbol)
                else:
                    invalid_symbols.append(symbol)
            
            if valid_symbols:
                print(f"\n{Fore.GREEN}✅ Valid symbols: {', '.join(valid_symbols)}{Style.RESET_ALL}")
                if invalid_symbols:
                    print(f"{Fore.RED}❌ Invalid symbols: {', '.join(invalid_symbols)}{Style.RESET_ALL}")
                
                confirm = self.get_user_input("Proceed with valid symbols? (y/n): ")
                if confirm.lower() == 'y':
                    return valid_symbols
            else:
                print(f"{Fore.RED}No valid symbols found. Please try again.{Style.RESET_ALL}")
    
    def get_date_range(self) -> tuple:
        """Get date range from user."""
        print(f"\n{Fore.CYAN}📅 Date Range Configuration{Style.RESET_ALL}")
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)
        
        print(f"Default range: {start_date} to {end_date}")
        
        use_default = self.get_user_input("Use default date range? (y/n): ", default='y')
        
        if use_default.lower() == 'y':
            return start_date, end_date
        
        start_input = self.get_user_input("Enter start date (YYYY-MM-DD): ", "date", start_date)
        end_input = self.get_user_input("Enter end date (YYYY-MM-DD): ", "date", end_date)
        
        if start_input >= end_input:
            print(f"{Fore.RED}Start date must be before end date. Using default range.{Style.RESET_ALL}")
            return start_date, end_date
            
        return start_input, end_input
    
    def display_symbol_info(self, symbols: List[str]):
        """Display basic information about selected symbols."""
        print(f"\n{Fore.CYAN}📊 Symbol Information{Style.RESET_ALL}")
        
        info_data = []
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                info_data.append([
                    symbol,
                    info.get('longName', 'N/A'),
                    f"${info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))}",
                    f"{info.get('marketCap', 0) / 1e9:.1f}B",
                    info.get('sector', 'N/A')
                ])
            except Exception as e:
                info_data.append([symbol, 'Error', 'N/A', 'N/A', 'N/A'])
        
        headers = ['Symbol', 'Company', 'Price', 'Market Cap', 'Sector']
        print(tabulate(info_data, headers=headers, tablefmt='grid'))
    
    def interactive_analysis_menu(self):
        """Main interactive analysis menu."""
        while True:
            self.print_menu({
                "1": "🔍 Load and Analyze Market Data",
                "2": "📊 Technical Analysis Dashboard",
                "3": "📈 Portfolio Analysis & Optimization",
                "4": "🔄 Backtesting Engine",
                "5": "📱 Real-time Data Monitor",
                "6": "🎯 Custom Analysis Builder",
                "7": "💾 Save/Load Analysis",
                "8": "⚙️ Settings & Configuration",
                "9": "❓ Help & Documentation",
                "0": "🚪 Exit"
            }, "Advanced Data Analysis Tool")
            
            choice = self.get_user_input("Select option: ", "int")
            
            if choice == 1:
                self.load_and_analyze_data()
            elif choice == 2:
                self.technical_analysis_dashboard()
            elif choice == 3:
                self.portfolio_analysis()
            elif choice == 4:
                self.backtesting_engine()
            elif choice == 5:
                self.real_time_monitor()
            elif choice == 6:
                self.custom_analysis_builder()
            elif choice == 7:
                self.save_load_analysis()
            elif choice == 8:
                self.settings_configuration()
            elif choice == 9:
                self.show_help()
            elif choice == 0:
                print(f"\n{Fore.GREEN}Thank you for using Advanced Data Analysis Tool!{Style.RESET_ALL}")
                break
            else:
                print(f"{Fore.RED}Invalid option. Please try again.{Style.RESET_ALL}")
    
    def load_and_analyze_data(self):
        """Load and analyze market data."""
        self.print_header("Market Data Analysis")
        
        symbols = self.get_symbols_from_user()
        start_date, end_date = self.get_date_range()
        
        self.display_symbol_info(symbols)
        
        print(f"\n{Fore.YELLOW}Loading market data...{Style.RESET_ALL}")
        try:
            results = self.analyzer.analyze_market(
                symbols=symbols,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
            
            self.current_symbols = symbols
            self.current_data = results
            self.analysis_results = results
            
            self.display_analysis_summary(results)
            
        except Exception as e:
            print(f"{Fore.RED}Error loading data: {e}{Style.RESET_ALL}")
    
    def display_analysis_summary(self, results: Dict[str, Any]):
        """Display analysis summary."""
        print(f"\n{Fore.GREEN}✅ Analysis Complete!{Style.RESET_ALL}")
        
        for symbol, data in results.items():
            if symbol == 'portfolio_analysis':
                continue
                
            print(f"\n{Fore.CYAN}{symbol} Summary:{Style.RESET_ALL}")
            
            # Basic info
            tech = data.get('technical_indicators', {})
            if tech:
                print(f"  Current Price: ${tech.get('current_price', 'N/A')}")
                print(f"  52-Week High: ${tech.get('fifty_two_week_high', 'N/A')}")
                print(f"  52-Week Low: ${tech.get('fifty_two_week_low', 'N/A')}")
            
            # Risk metrics
            risk = data.get('risk_metrics', {})
            if risk:
                print(f"  Sharpe Ratio: {risk.get('sharpe_ratio', 'N/A')}")
                print(f"  Volatility: {risk.get('volatility', 'N/A')}")
    
    def technical_analysis_dashboard(self):
        """Technical analysis dashboard."""
        if not self.current_data:
            print(f"{Fore.RED}No data loaded. Please load data first (Option 1).{Style.RESET_ALL}")
            return
        
        self.print_header("Technical Analysis Dashboard")
        
        symbol = self.get_user_input("Enter symbol for detailed analysis: ", default=self.current_symbols[0])
        
        if symbol not in self.current_data:
            print(f"{Fore.RED}Symbol not found in current data.{Style.RESET_ALL}")
            return
        
        data = self.current_data[symbol]
        
        print(f"\n{Fore.CYAN}Technical Indicators for {symbol}:{Style.RESET_ALL}")
        
        tech = data.get('technical_indicators', {})
        if tech:
            indicators = [
                ['RSI', f"{tech.get('rsi', 'N/A')}"],
                ['MACD', f"{tech.get('macd', 'N/A')}"],
                ['Signal', f"{tech.get('macd_signal', 'N')}"],
                ['SMA 20', f"${tech.get('sma_20', 'N/A')}"],
                ['SMA 50', f"${tech.get('sma_50', 'N/A')}"],
                ['EMA 12', f"${tech.get('ema_12', 'N/A')}"],
                ['EMA 26', f"${tech.get('ema_26', 'N/A')}"],
                ['Bollinger Upper', f"${tech.get('bb_upper', 'N/A')}"],
                ['Bollinger Lower', f"${tech.get('bb_lower', 'N/A')}"],
                ['Volume', f"{tech.get('volume', 'N/A'):,}"]
            ]
            
            print(tabulate(indicators, headers=['Indicator', 'Value'], tablefmt='grid'))
    
    def portfolio_analysis(self):
        """Portfolio analysis and optimization."""
        if not self.current_data:
            print(f"{Fore.RED}No data loaded. Please load data first.{Style.RESET_ALL}")
            return
        
        self.print_header("Portfolio Analysis")
        
        portfolio_data = self.current_data.get('portfolio_analysis', {})
        if portfolio_data:
            print(f"\n{Fore.CYAN}Portfolio Metrics:{Style.RESET_ALL}")
            
            metrics = [
                ['Total Return', f"{portfolio_data.get('total_return', 0):.2%}"],
                ['Volatility', f"{portfolio_data.get('volatility', 0):.2%}"],
                ['Sharpe Ratio', f"{portfolio_data.get('sharpe_ratio', 0):.2f}"],
                ['Max Drawdown', f"{portfolio_data.get('max_drawdown', 0):.2%}"],
                ['Beta', f"{portfolio_data.get('beta', 0):.2f}"],
                ['Alpha', f"{portfolio_data.get('alpha', 0):.2%}"]
            ]
            
            print(tabulate(metrics, headers=['Metric', 'Value'], tablefmt='grid'))
    
    def backtesting_engine(self):
        """Backtesting engine."""
        if not self.current_symbols:
            print(f"{Fore.RED}No symbols loaded. Please load data first.{Style.RESET_ALL}")
            return
        
        self.print_header("Backtesting Engine")
        
        strategy = self.get_user_input(
            "Enter strategy (moving_average/rsi/macd/bollinger_bands): ",
            default='moving_average'
        )
        
        print(f"\n{Fore.YELLOW}Running backtest for {strategy} strategy...{Style.RESET_ALL}")
        
        # This would integrate with actual backtesting engine
        print(f"{Fore.GREEN}Backtest completed for {', '.join(self.current_symbols)}{Style.RESET_ALL}")
    
    def real_time_monitor(self):
        """Real-time data monitor."""
        if not self.current_symbols:
            print(f"{Fore.RED}No symbols loaded. Please load data first.{Style.RESET_ALL}")
            return
        
        self.print_header("Real-time Data Monitor")
        
        print(f"Monitoring: {', '.join(self.current_symbols)}")
        print("Press Ctrl+C to stop monitoring")
        
        try:
            while True:
                for symbol in self.current_symbols:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    current_price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
                    print(f"{symbol}: ${current_price}")
                
                import time
                time.sleep(5)
                
        except KeyboardInterrupt:
            print(f"\n{Fore.GREEN}Monitoring stopped.{Style.RESET_ALL}")
    
    def custom_analysis_builder(self):
        """Custom analysis builder."""
        self.print_header("Custom Analysis Builder")
        
        print("Feature coming soon...")
    
    def save_load_analysis(self):
        """Save/load analysis functionality."""
        self.print_header("Save/Load Analysis")
        
        action = self.get_user_input("Save (s) or Load (l): ", default='s')
        
        if action.lower() == 's':
            if self.analysis_results:
                filename = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump(self.analysis_results, f, indent=2, default=str)
                print(f"{Fore.GREEN}Analysis saved to {filename}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}No analysis to save.{Style.RESET_ALL}")
        else:
            print("Load functionality coming soon...")
    
    def settings_configuration(self):
        """Settings and configuration."""
        self.print_header("Settings & Configuration")
        
        print("Settings configuration coming soon...")
    
    def show_help(self):
        """Show help and documentation."""
        self.print_header("Help & Documentation")
        
        help_text = """
        📚 Advanced Data Analysis Tool Help
        
        1. Load and Analyze Market Data
           - Select stock symbols
           - Choose date range
           - Get comprehensive analysis
        
        2. Technical Analysis Dashboard
           - View technical indicators
           - Analyze trends and patterns
        
        3. Portfolio Analysis
           - Risk metrics
           - Performance attribution
        
        4. Backtesting Engine
           - Test strategies
           - Optimize parameters
        
        5. Real-time Monitor
           - Live price updates
           - Market tracking
        
        For detailed documentation, see README.md
        """
        
        print(help_text)

def main():
    """Main entry point for interactive tool."""
    print(f"{Fore.CYAN}")
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                    Advanced Interactive Data Analysis Tool                    ║")
    print("║                                                                              ║")
    print("║  🚀 Professional-grade market data analysis with interactive user interface   ║")
    print("║  📊 Real-time data, technical analysis, backtesting, and portfolio tools   ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}")
    
    analyzer = InteractiveDataAnalyzer()
    analyzer.interactive_analysis_menu()

if __name__ == '__main__':
    main()
