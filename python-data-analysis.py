# python-data-analysis.py

# This advanced script downloads historical stock data, calculates multiple technical
# indicators (SMAs, Bollinger Bands), implements a backtesting strategy, and
# visualizes the results with multiple subplots. It also takes user input for
# the stock ticker and date range.

# --- Prerequisites ---
# Before running this script, you need to install the required libraries.
# You can do this by running the following command in your terminal:
# pip install yfinance pandas matplotlib

# --- Imports ---
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime

def run_analysis(ticker, start_date, end_date):
    """
    Main function to download, analyze, backtest, and visualize stock data.

    Args:
        ticker (str): The stock symbol (e.g., "AAPL").
        start_date (str): The start date for the data in "YYYY-MM-DD" format.
        end_date (str): The end date for the data in "YYYY-MM-DD" format.
    """
    # --- Data Acquisition ---
    try:
        print(f"\nDownloading data for {ticker} from {start_date} to {end_date}...")
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        if stock_data.empty:
            raise ValueError("No data found for the specified ticker and date range.")
        print("Download complete.")
    except Exception as e:
        print(f"An error occurred while downloading data: {e}")
        return

    # --- Data Analysis: Technical Indicators ---
    # Calculate daily returns first, as other sections depend on it.
    stock_data['Daily Return'] = stock_data['Close'].pct_change()

    stock_data['20-Day SMA'] = stock_data['Close'].rolling(window=20).mean()
    stock_data['50-Day SMA'] = stock_data['Close'].rolling(window=50).mean()

    # Calculate Bollinger Bands
    stock_data['STD'] = stock_data['Close'].rolling(window=20).std()
    stock_data['Upper Band'] = stock_data['20-Day SMA'] + (stock_data['STD'] * 2)
    stock_data['Lower Band'] = stock_data['20-Day SMA'] - (stock_data['STD'] * 2)

    # --- Backtesting a Simple Strategy ---
    # Strategy: Buy when the 20-day SMA crosses above the 50-day SMA.
    # We will simulate trading to calculate strategy returns.
    stock_data['Signal'] = 0.0
    stock_data['Signal'][20:] = (stock_data['20-Day SMA'][20:] > stock_data['50-Day SMA'][20:]).astype(float)
    stock_data['Position'] = stock_data['Signal'].diff()
    
    # Calculate daily returns for the strategy and a simple buy-and-hold.
    stock_data['Strategy Returns'] = stock_data['Daily Return'].shift(-1) * stock_data['Signal']
    stock_data['Buy and Hold Returns'] = stock_data['Daily Return'].shift(-1)

    # Calculate cumulative returns.
    stock_data['Cumulative Strategy Returns'] = (1 + stock_data['Strategy Returns']).cumprod() - 1
    stock_data['Cumulative Buy and Hold Returns'] = (1 + stock_data['Buy and Hold Returns']).cumprod() - 1

    # --- Data Visualization ---
    # Create a figure with three subplots.
    fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, ncols=1, figsize=(14, 16), sharex=True)

    # --- Subplot 1: Price, SMAs, Bollinger Bands, and Signals ---
    ax1.plot(stock_data['Close'], label='Closing Price', color='blue', linewidth=1.5)
    ax1.plot(stock_data['20-Day SMA'], label='20-Day SMA', color='orange', linestyle='--')
    ax1.plot(stock_data['50-Day SMA'], label='50-Day SMA', color='red', linestyle='--')
    ax1.plot(stock_data['Upper Band'], label='Upper Bollinger Band', color='gray', linestyle=':')
    ax1.plot(stock_data['Lower Band'], label='Lower Bollinger Band', color='gray', linestyle=':')

    # Plot the buy signals.
    ax1.plot(stock_data.loc[stock_data['Position'] == 1.0].index, 
             stock_data['20-Day SMA'][stock_data['Position'] == 1.0],
             '^', markersize=10, color='g', label='Buy Signal')

    # Plot the sell signals.
    ax1.plot(stock_data.loc[stock_data['Position'] == -1.0].index, 
             stock_data['20-Day SMA'][stock_data['Position'] == -1.0],
             'v', markersize=10, color='r', label='Sell Signal')
             
    ax1.set_title(f'Stock Price & Strategy Signals for {ticker}', fontsize=16)
    ax1.set_ylabel('Price (USD)', fontsize=12)
    ax1.legend()
    ax1.grid(True, linestyle='--', alpha=0.6)

    # --- Subplot 2: Daily Returns ---
    ax2.bar(stock_data.index, stock_data['Daily Return'], label='Daily Return', color='gray', alpha=0.6)
    ax2.set_title('Daily Returns', fontsize=16)
    ax2.set_ylabel('Return (%)', fontsize=12)
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend()
    
    # --- Subplot 3: Strategy vs. Buy and Hold Performance ---
    ax3.plot(stock_data['Cumulative Strategy Returns'], label='Strategy Performance', color='green', linewidth=2)
    ax3.plot(stock_data['Cumulative Buy and Hold Returns'], label='Buy & Hold Performance', color='purple', linewidth=2, linestyle='--')
    ax3.set_title('Strategy Backtesting Performance', fontsize=16)
    ax3.set_xlabel('Date', fontsize=12)
    ax3.set_ylabel('Cumulative Return', fontsize=12)
    ax3.legend()
    ax3.grid(True, linestyle='--', alpha=0.6)

    # Improve layout and save the plot.
    plt.tight_layout()
    plot_filename = f"{ticker}_advanced_analysis.png"
    plt.savefig(plot_filename)
    print(f"\nPlot saved to '{plot_filename}'")
    plt.show()

if __name__ == '__main__':
    # --- User Input ---
    print("Welcome to the advanced stock analysis tool!")
    print("------------------------------------------")
    ticker = input("Enter a stock ticker (e.g., AAPL): ").upper()
    start_date = input("Enter the start date (YYYY-MM-DD): ")
    end_date = input("Enter the end date (YYYY-MM-DD): ")
    
    # Validate date formats.
    try:
        datetime.datetime.strptime(start_date, "%Y-%m-%d")
        datetime.datetime.strptime(end_date, "%Y-%m-%d")
        run_analysis(ticker, start_date, end_date)
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
