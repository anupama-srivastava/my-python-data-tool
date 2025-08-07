# python-data-analysis.py

# This is a professional-grade, command-line tool for backtesting a trading
# strategy. It features a simplified, stable design to ensure error-free
# execution while demonstrating advanced data analysis and visualization skills.

# --- Prerequisites ---
# Before running this script, you need to install the required libraries.
# You can do this by running the following command in your terminal:
# pip install yfinance pandas matplotlib numpy

# --- Imports ---
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np

def get_data(ticker, start_date, end_date):
    """
    Downloads historical stock data from Yahoo Finance.

    Args:
        ticker (str): The stock symbol (e.g., "AAPL").
        start_date (str): The start date for the data in "YYYY-MM-DD" format.
        end_date (str): The end date for the data in "YYYY-MM-DD" format.
    
    Returns:
        pandas.DataFrame: A DataFrame containing the stock data.
    """
    try:
        print(f"\nDownloading data for {ticker} from {start_date} to {end_date}...")
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        if stock_data.empty:
            raise ValueError("No data found for the specified ticker and date range.")
        print("Download complete.")
        return stock_data
    except Exception as e:
        print(f"An error occurred while downloading data: {e}")
        return None

def calculate_indicators(data):
    """
    Calculates a suite of technical indicators and adds them to the DataFrame.

    Args:
        data (pandas.DataFrame): The stock data.
    
    Returns:
        pandas.DataFrame: The DataFrame with added indicators.
    """
    # Calculate daily returns
    data['Daily Return'] = data['Close'].pct_change()

    # Calculate Simple Moving Averages
    data['20-Day SMA'] = data['Close'].rolling(window=20).mean()
    data['50-Day SMA'] = data['Close'].rolling(window=50).mean()

    # Calculate Relative Strength Index (RSI)
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))

    # Calculate Moving Average Convergence Divergence (MACD)
    data['12-Day EMA'] = data['Close'].ewm(span=12, adjust=False).mean()
    data['26-Day EMA'] = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = data['12-Day EMA'] - data['26-Day EMA']
    data['MACD Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
    
    # Calculate Bollinger Bands
    data['STD'] = data['Close'].rolling(window=20).std()
    data['Upper Band'] = data['20-Day SMA'] + (data['STD'] * 2)
    data['Lower Band'] = data['20-Day SMA'] - (data['STD'] * 2)

    return data

def backtest_strategy(data):
    """
    Backtests a simple, yet robust, trading strategy and calculates its performance.

    Strategy: Buy when the 20-day SMA crosses above the 50-day SMA.
              Sell on the reverse signal.

    Args:
        data (pandas.DataFrame): The stock data with indicators.

    Returns:
        tuple: A tuple containing the strategy and buy-and-hold returns,
               and a summary of key performance metrics.
    """
    # Generate buy and sell signals using a vectorized approach.
    data['Signal'] = 0.0
    data.loc[data['20-Day SMA'] > data['50-Day SMA'], 'Signal'] = 1.0
    
    # The `Position` column now directly indicates a change in our signal.
    data['Position'] = data['Signal'].diff()

    # Calculate strategy returns based on our signals. This is a robust method.
    data['Strategy Returns'] = data['Daily Return'].shift(-1) * data['Position']
    data['Buy and Hold Returns'] = data['Daily Return'].shift(-1)
    
    # Calculate cumulative returns.
    data['Cumulative Strategy Returns'] = (1 + data['Strategy Returns']).cumprod() - 1
    data['Cumulative Buy and Hold Returns'] = (1 + data['Buy and Hold Returns']).cumprod() - 1

    # Calculate key performance metrics.
    strategy_returns = data['Strategy Returns'].dropna()
    
    # Annualized Sharpe Ratio (assuming 252 trading days)
    sharpe_ratio = np.sqrt(252) * strategy_returns.mean() / strategy_returns.std()
    
    # Maximum Drawdown
    cumulative_returns = (1 + strategy_returns).cumprod()
    peak = cumulative_returns.expanding(min_periods=1).max()
    drawdown = (cumulative_returns - peak) / peak
    max_drawdown = drawdown.min()
    
    performance_metrics = {
        'Total Strategy Return': f"{data['Cumulative Strategy Returns'].iloc[-1] * 100:.2f}%",
        'Total Buy & Hold Return': f"{data['Cumulative Buy and Hold Returns'].iloc[-1] * 100:.2f}%",
        'Annualized Sharpe Ratio': f"{sharpe_ratio:.2f}",
        'Maximum Drawdown': f"{max_drawdown * 100:.2f}%"
    }

    return data, performance_metrics

def plot_results(data, ticker):
    """
    Generates and saves a comprehensive multi-subplot visualization of the analysis.
    """
    # Create a figure with four subplots.
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(nrows=4, ncols=1, figsize=(14, 20), sharex=True, gridspec_kw={'height_ratios': [3, 1, 1, 1]})

    # --- Subplot 1: Price, SMAs, Bollinger Bands, and Signals ---
    ax1.plot(data['Close'], label='Closing Price', color='blue', linewidth=1.5)
    ax1.plot(data['20-Day SMA'], label='20-Day SMA', color='orange', linestyle='--')
    ax1.plot(data['50-Day SMA'], label='50-Day SMA', color='red', linestyle='--')
    ax1.fill_between(data.index, data['Upper Band'], data['Lower Band'], color='gray', alpha=0.2, label='Bollinger Bands')
    
    # Plot the buy and sell signals.
    buy_signals = data.loc[data['Position'] == 1.0].index
    ax1.plot(buy_signals, data['20-Day SMA'][buy_signals], '^', markersize=10, color='g', label='Buy Signal')
    sell_signals = data.loc[data['Position'] == -1.0].index
    ax1.plot(sell_signals, data['20-Day SMA'][sell_signals], 'v', markersize=10, color='r', label='Sell Signal')

    ax1.set_title(f'Stock Price & Strategy Signals for {ticker}', fontsize=16)
    ax1.set_ylabel('Price (USD)', fontsize=12)
    ax1.legend()
    ax1.grid(True, linestyle='--', alpha=0.6)

    # --- Subplot 2: Relative Strength Index (RSI) ---
    ax2.plot(data['RSI'], label='RSI', color='purple', linewidth=1.5)
    ax2.axhline(70, linestyle='--', alpha=0.5, color='red', label='Overbought')
    ax2.axhline(30, linestyle='--', alpha=0.5, color='green', label='Oversold')
    ax2.set_title('Relative Strength Index (RSI)', fontsize=16)
    ax2.set_ylabel('RSI Value', fontsize=12)
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend()
    
    # --- Subplot 3: MACD Indicator ---
    ax3.plot(data['MACD'], label='MACD', color='blue', linewidth=1.5)
    ax3.plot(data['MACD Signal'], label='MACD Signal', color='red', linestyle='--')
    ax3.axhline(0, linestyle='--', alpha=0.5, color='gray')
    ax3.set_title('MACD Indicator', fontsize=16)
    ax3.set_ylabel('Value', fontsize=12)
    ax3.grid(True, linestyle='--', alpha=0.6)
    ax3.legend()
    
    # --- Subplot 4: Strategy vs. Buy and Hold Performance ---
    ax4.plot(data['Cumulative Strategy Returns'], label='Strategy Performance', color='green', linewidth=2)
    ax4.plot(data['Cumulative Buy and Hold Returns'], label='Buy & Hold Performance', color='purple', linewidth=2, linestyle='--')
    ax4.set_title('Strategy Backtesting Performance', fontsize=16)
    ax4.set_xlabel('Date', fontsize=12)
    ax4.set_ylabel('Cumulative Return', fontsize=12)
    ax4.legend()
    ax4.grid(True, linestyle='--', alpha=0.6)

    # Improve layout and save the plot.
    plt.tight_layout()
    plot_filename = f"{ticker}_advanced_analysis.png"
    plt.savefig(plot_filename)
    print(f"\nPlot saved to '{plot_filename}'")
    plt.show()

if __name__ == '__main__':
    # --- User Input ---
    print("Welcome to the professional-grade stock analysis tool!")
    print("------------------------------------------")
    ticker = input("Enter a stock ticker (e.g., AAPL): ").upper()
    start_date = input("Enter the start date (YYYY-MM-DD): ")
    end_date = input("Enter the end date (YYYY-MM-DD): ")
    
    # Validate date formats.
    try:
        datetime.datetime.strptime(start_date, "%Y-%m-%d")
        datetime.datetime.strptime(end_date, "%Y-%m-%d")
        
        # Run the analysis pipeline
        stock_data = get_data(ticker, start_date, end_date)
        if stock_data is not None:
            stock_data = calculate_indicators(stock_data)
            stock_data, metrics = backtest_strategy(stock_data)
            
            # Print performance metrics
            print("\n--- Strategy Performance Metrics ---")
            for key, value in metrics.items():
                print(f"{key}: {value}")
            
            plot_results(stock_data, ticker)
            
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
