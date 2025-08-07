# python-data-analysis.py

# This is a professional-grade, command-line tool for backtesting a trading
# strategy. It features a simplified, stable design to ensure error-free
# execution while demonstrating advanced data analysis and visualization skills.

# --- Prerequisites ---
# Before running this script, you need to install the required libraries.
# You can do this by running the following command in your terminal:
# pip install yfinance pandas matplotlib numpy mplfinance

# --- Imports ---
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np
import mplfinance as mpf

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

    # Provide conversational feedback for buy and sell signals.
    buy_signals = data.loc[data['Position'] == 1.0]
    sell_signals = data.loc[data['Position'] == -1.0]

    if not buy_signals.empty:
        print("\n--- Trading Signals ---")
        for date, row in buy_signals.iterrows():
            print(f"🟢 BUY Signal: The 20-day SMA crossed above the 50-day SMA on {date.strftime('%Y-%m-%d')}.")
    else:
        print("\n--- Trading Signals ---")
        print("No BUY signals were generated in this period.")
        
    if not sell_signals.empty:
        for date, row in sell_signals.iterrows():
            print(f"🔴 SELL Signal: The 20-day SMA crossed below the 50-day SMA on {date.strftime('%Y-%m-%d')}.")
    else:
        print("No SELL signals were generated in this period.")

    # Calculate strategy returns based on our signals. This is a robust method.
    data['Strategy Returns'] = data['Daily Return'].shift(-1) * data['Position']
    data['Buy and Hold Returns'] = data['Daily Return'].shift(-1)
    
    # Calculate cumulative returns.
    data['Cumulative Strategy Returns'] = (1 + data['Strategy Returns']).cumprod() - 1
    data['Cumulative Buy and Hold Returns'] = (1 + data['Buy and Hold Returns']).cumprod() - 1

    # Calculate key performance metrics.
    strategy_returns = data['Strategy Returns'].dropna()
    
    # Annualized Sharpe Ratio (assuming 252 trading days)
    sharpe_ratio = np.sqrt(252) * strategy_returns.mean() / strategy_returns.std() if not strategy_returns.empty and strategy_returns.std() != 0 else 0.0
    
    # Maximum Drawdown
    cumulative_returns = (1 + strategy_returns).cumprod()
    peak = cumulative_returns.expanding(min_periods=1).max()
    drawdown = (cumulative_returns - peak) / peak
    max_drawdown = drawdown.min() if not drawdown.empty and not pd.isna(drawdown.min()) else 0.0
    
    total_strategy_return = data['Cumulative Strategy Returns'].iloc[-1] if not data['Cumulative Strategy Returns'].empty and not pd.isna(data['Cumulative Strategy Returns'].iloc[-1]) else 0.0
    total_buy_hold_return = data['Cumulative Buy and Hold Returns'].iloc[-1] if not data['Cumulative Buy and Hold Returns'].empty and not pd.isna(data['Cumulative Buy and Hold Returns'].iloc[-1]) else 0.0

    performance_metrics = {
        'Total Strategy Return': f"{total_strategy_return * 100:.2f}%",
        'Total Buy & Hold Return': f"{total_buy_hold_return * 100:.2f}%",
        'Annualized Sharpe Ratio': f"{sharpe_ratio:.2f}",
        'Maximum Drawdown': f"{max_drawdown * 100:.2f}%"
    }

    return data, performance_metrics

def plot_results(data, ticker):
    """
    Generates and saves a comprehensive multi-subplot visualization of the analysis.
    """
    # Plot the candlestick chart with indicators
    apds = [
        mpf.make_addplot(data['20-Day SMA'], color='orange', panel=0),
        mpf.make_addplot(data['50-Day SMA'], color='red', panel=0),
        mpf.make_addplot(data['Upper Band'], color='gray', linestyle='--', panel=0),
        mpf.make_addplot(data['Lower Band'], color='gray', linestyle='--', panel=0),
        mpf.make_addplot(data['RSI'], color='purple', panel=1),
        mpf.make_addplot(data['MACD'], color='blue', panel=2),
        mpf.make_addplot(data['MACD Signal'], color='red', panel=2),
    ]

    buy_signals = data.loc[data['Position'] == 1.0].index
    sell_signals = data.loc[data['Position'] == -1.0].index
    
    buy_markers = pd.Series('^', index=buy_signals)
    sell_markers = pd.Series('v', index=sell_signals)

    markers = pd.concat([buy_markers, sell_markers]).sort_index()
    colors = ['g' if marker == '^' else 'r' for marker in markers]
    
    apds.append(mpf.make_addplot(data.loc[markers.index, '20-Day SMA'], type='scatter', markersize=100, marker=markers.values, color=colors, panel=0))

    style = mpf.make_mpf_style(base_mpl_style='dark_background', marketcolors=mpf.make_marketcolors(up='g', down='r'))
    
    mpf.plot(data, type='candle', addplot=apds, style=style,
             title=f'Technical Analysis for {ticker}', ylabel='Price (USD)',
             volume=True, panel_ratios=(4, 1, 1, 1), savefig=f"{ticker}_analysis_candlestick.png")

    # Plot the performance chart separately using matplotlib
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.plot(data['Cumulative Strategy Returns'], label='Strategy Performance', color='green', linewidth=2)
    ax.plot(data['Cumulative Buy and Hold Returns'], label='Buy & Hold Performance', color='purple', linewidth=2, linestyle='--')
    ax.set_title(f'Strategy Backtesting Performance (Cumulative Returns) for {ticker}', fontsize=16)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Cumulative Return', fontsize=12)
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)
    
    performance_filename = f"{ticker}_performance_chart.png"
    fig.savefig(performance_filename)
    
    # Displaying the plots
    print(f"Candlestick chart saved to '{ticker}_analysis_candlestick.png'")
    print(f"Performance chart saved to '{performance_filename}'")
    
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
