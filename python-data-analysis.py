# python-data-analysis.py

# This is a professional-grade, multi-faceted stock analysis tool.
# It features a robust GUI built with tkinter, enabling users to perform
# sophisticated backtesting with realistic trading mechanics and a
# comprehensive visualization of key performance indicators. The code is
# structured modularly for clarity and future extensibility.

# --- Prerequisites ---
# Before running this script, you need to install the required libraries.
# You can do this by running the following command in your terminal:
# pip install yfinance pandas matplotlib numpy

# --- Imports ---
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import datetime
import numpy as np

# --- Core Functions ---

def get_data(ticker, start_date, end_date):
    """
    Downloads historical stock data from Yahoo Finance.
    """
    try:
        print(f"\nDownloading data for {ticker} from {start_date} to {end_date}...")
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        if stock_data.empty:
            raise ValueError("No data found for the specified ticker and date range.")
        print("Download complete.")
        return stock_data
    except Exception as e:
        messagebox.showerror("Download Error", f"An error occurred while downloading data: {e}")
        return None

def calculate_indicators(data):
    """
    Calculates a suite of technical indicators and adds them to the DataFrame.
    """
    data['Daily Return'] = data['Close'].pct_change()
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

    # Generate signals for backtesting
    data['Signal'] = 0.0
    data.loc[data['20-Day SMA'] > data['50-Day SMA'], 'Signal'] = 1.0
    data.loc[data['RSI'] > 70, 'Signal'] = 0.0
    data['Position'] = data['Signal'].diff()

    return data

def backtest_strategy(data, log_widget):
    """
    Backtests a sophisticated trading strategy with dynamic stop-loss, take-profit,
    and detailed position management.
    """
    initial_cash = 100000
    portfolio = initial_cash
    in_position = False
    shares_to_buy = 0
    entry_price = 0
    
    transaction_cost_rate = 0.001

    # Drop rows with NaN values to ensure all indicators are calculated
    data = data.dropna().copy()
    
    log_widget.insert(tk.END, "Starting backtest...\n\n")

    trade_log = []
    
    for i in range(len(data)):
        # Check for a BUY signal
        buy_signal = (data['Position'].iloc[i] == 1.0)
        
        # Check for a SELL signal
        sell_signal = (data['Position'].iloc[i] == -1.0)

        # Check for stop-loss or take-profit
        current_price = data['Close'].iloc[i]
        is_stop_loss = in_position and current_price < entry_price * (1 - 0.05)
        is_take_profit = in_position and current_price > entry_price * (1 + 0.10)

        if buy_signal:
            entry_price = data['Close'].iloc[i]
            position_size = portfolio * 0.5  # Allocate 50% of portfolio
            shares_to_buy = int(position_size / entry_price)
            cost = shares_to_buy * entry_price
            transaction_cost = cost * transaction_cost_rate
            portfolio -= (cost + transaction_cost)
            in_position = True
            log_widget.insert(tk.END, f"BUY signal on {data.index[i].strftime('%Y-%m-%d')} at ${entry_price:.2f}\n")
            trade_log.append({'date': data.index[i], 'action': 'BUY', 'price': entry_price, 'portfolio': portfolio})
        
        elif sell_signal or is_stop_loss or is_take_profit:
            if in_position:
                revenue = shares_to_buy * current_price
                transaction_cost = revenue * transaction_cost_rate
                portfolio += (revenue - transaction_cost)
                in_position = False
                
                if is_stop_loss:
                    log_widget.insert(tk.END, f"STOP-LOSS on {data.index[i].strftime('%Y-%m-%d')} at ${current_price:.2f}\n")
                elif is_take_profit:
                    log_widget.insert(tk.END, f"TAKE-PROFIT on {data.index[i].strftime('%Y-%m-%d')} at ${current_price:.2f}\n")
                else:
                    log_widget.insert(tk.END, f"SELL signal on {data.index[i].strftime('%Y-%m-%d')} at ${current_price:.2f}\n")
                
                trade_log.append({'date': data.index[i], 'action': 'SELL', 'price': current_price, 'portfolio': portfolio})

    # --- Calculate Final Metrics ---
    trade_df = pd.DataFrame(trade_log)
    if not trade_df.empty:
        trade_df.set_index('date', inplace=True)
        
        buy_hold_returns = (data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1

        final_portfolio_value = portfolio
        total_strategy_return = (final_portfolio_value / initial_cash) - 1
        
        daily_returns = trade_df['portfolio'].pct_change().dropna()
        if not daily_returns.empty:
            sharpe_ratio = np.sqrt(252) * daily_returns.mean() / daily_returns.std()
            
            cumulative_returns = (1 + daily_returns).cumprod()
            peak = cumulative_returns.expanding(min_periods=1).max()
            drawdown = (cumulative_returns - peak) / peak
            max_drawdown = drawdown.min()
        else:
            sharpe_ratio = 0.0
            max_drawdown = 0.0

    else:
        final_portfolio_value = initial_cash
        total_strategy_return = 0.0
        buy_hold_returns = (data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1
        sharpe_ratio = 0.0
        max_drawdown = 0.0

    performance_metrics = {
        'Final Portfolio Value': f"${final_portfolio_value:.2f}",
        'Total Strategy Return': f"{total_strategy_return * 100:.2f}%",
        'Total Buy & Hold Return': f"{buy_hold_returns * 100:.2f}%",
        'Annualized Sharpe Ratio': f"{sharpe_ratio:.2f}",
        'Maximum Drawdown': f"{max_drawdown * 100:.2f}%"
    }

    # Recalculate cumulative returns for plotting
    data['Strategy Cumulative Returns'] = (data['Close'] / data['Close'].iloc[0]) * (final_portfolio_value / initial_cash) - 1
    data['Buy and Hold Cumulative Returns'] = (data['Close'] / data['Close'].iloc[0]) - 1

    return data, performance_metrics

def plot_results(data, ticker, plot_frame, file_path=None):
    """
    Generates a multi-subplot visualization and embeds it into the GUI.
    """
    for widget in plot_frame.winfo_children():
        widget.destroy()
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(nrows=5, ncols=1, figsize=(14, 22), sharex=True, gridspec_kw={'height_ratios': [3, 1, 1, 1, 1]})
    
    # --- Subplot 1: Price, SMAs, Bollinger Bands, and Signals ---
    ax1.plot(data['Close'], label='Closing Price', color='white', linewidth=1.5)
    ax1.plot(data['20-Day SMA'], label='20-Day SMA', color='orange', linestyle='--')
    ax1.plot(data['50-Day SMA'], label='50-Day SMA', color='red', linestyle='--')
    ax1.fill_between(data.index, data['Upper Band'], data['Lower Band'], color='gray', alpha=0.2, label='Bollinger Bands')
    buy_signals = data.loc[data['Position'] == 1.0].index
    ax1.plot(buy_signals, data['20-Day SMA'][buy_signals], '^', markersize=10, color='lime', label='Buy Signal')
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
    ax2.legend()

    # --- Subplot 3: MACD Indicator ---
    ax3.plot(data['MACD'], label='MACD', color='blue', linewidth=1.5)
    ax3.plot(data['MACD Signal'], label='MACD Signal', color='red', linestyle='--')
    ax3.axhline(0, linestyle='--', alpha=0.5, color='gray')
    ax3.set_title('MACD Indicator', fontsize=16)
    ax3.set_ylabel('Value', fontsize=12)
    ax3.legend()
    
    # --- Subplot 4: Bollinger Bands
    ax4.plot(data['Close'], label='Closing Price', color='white', linewidth=1.5)
    ax4.plot(data['Upper Band'], label='Upper Band', color='lime', linestyle='--')
    ax4.plot(data['Lower Band'], label='Lower Band', color='magenta', linestyle='--')
    ax4.set_title('Bollinger Bands', fontsize=16)
    ax4.set_ylabel('Price (USD)', fontsize=12)
    ax4.legend()

    # --- Subplot 5: Strategy vs. Buy and Hold Performance ---
    ax5.plot(data['Strategy Cumulative Returns'], label='Strategy Performance', color='lime', linewidth=2)
    ax5.plot(data['Buy and Hold Cumulative Returns'], label='Buy & Hold Performance', color='magenta', linewidth=2, linestyle='--')
    ax5.set_title('Strategy Backtesting Performance', fontsize=16)
    ax5.set_xlabel('Date', fontsize=12)
    ax5.set_ylabel('Cumulative Return', fontsize=12)
    ax5.legend()
    
    plt.tight_layout()

    if file_path:
        fig.savefig(file_path)
        messagebox.showinfo("Save Plot", f"Plot saved to:\n{file_path}")
    else:
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        canvas.draw()
    plt.close(fig)

def save_plot_as_image(plot_frame, data, ticker):
    """
    Saves the currently displayed plot to a file chosen by the user.
    """
    file_path = filedialog.asksaveasfilename(defaultextension=".png", 
                                             filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
    if file_path:
        plot_results(data, ticker, plot_frame, file_path)

def run_analysis(ticker_entry, start_date_entry, end_date_entry, plot_frame, metrics_label, log_widget, save_button):
    """
    Orchestrates the entire analysis pipeline from the GUI.
    """
    log_widget.delete(1.0, tk.END)
    metrics_label.config(text="--- Strategy Performance Metrics ---")
    ticker = ticker_entry.get().upper()
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()

    if not ticker or not start_date or not end_date:
        messagebox.showerror("Input Error", "All fields are required.")
        return

    try:
        datetime.datetime.strptime(start_date, "%Y-%m-%d")
        datetime.datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Date Format Error", "Invalid date format. Please use YYYY-MM-DD.")
        return

    stock_data = get_data(ticker, start_date, end_date)
    if stock_data is not None:
        stock_data = calculate_indicators(stock_data)
        stock_data, metrics = backtest_strategy(stock_data, log_widget)
        
        metrics_text = "--- Strategy Performance Metrics ---\n"
        for key, value in metrics.items():
            metrics_text += f"{key}: {value}\n"
        metrics_label.config(text=metrics_text)

        plot_results(stock_data, ticker, plot_frame)
        save_button.config(command=lambda: save_plot_as_image(plot_frame, stock_data, ticker))

def create_gui():
    """
    Sets up and runs the main GUI application window.
    """
    root = tk.Tk()
    root.title("Professional-Grade Stock Analysis Tool")
    root.geometry("1800x1200")

    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=3)
    main_frame.rowconfigure(0, weight=1)

    # --- Left Panel for Inputs and Log ---
    left_panel = ttk.Frame(main_frame, padding="10")
    left_panel.grid(row=0, column=0, sticky="nsew")
    left_panel.rowconfigure(2, weight=1)

    input_frame = ttk.Frame(left_panel)
    input_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(input_frame, text="Stock Ticker:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
    ticker_entry = ttk.Entry(input_frame, width=10)
    ticker_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)
    ticker_entry.insert(0, "MSFT")

    ttk.Label(input_frame, text="Start Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
    start_date_entry = ttk.Entry(input_frame, width=15)
    start_date_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)
    start_date_entry.insert(0, (datetime.date.today() - datetime.timedelta(days=730)).strftime("%Y-%m-%d"))

    ttk.Label(input_frame, text="End Date (YYYY-MM-DD):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
    end_date_entry = ttk.Entry(input_frame, width=15)
    end_date_entry.grid(row=2, column=1, sticky="w", padx=5, pady=2)
    end_date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

    button_frame = ttk.Frame(input_frame)
    button_frame.grid(row=3, column=0, columnspan=2, pady=10)

    run_button = ttk.Button(button_frame, text="Run Analysis")
    run_button.pack(side=tk.LEFT, padx=5)
    
    save_button = ttk.Button(button_frame, text="Save Plot")
    save_button.pack(side=tk.LEFT, padx=5)

    metrics_label = ttk.Label(left_panel, text="", font=("Arial", 12))
    metrics_label.pack(pady=10)
    
    ttk.Label(left_panel, text="Trade Log:").pack(pady=5, anchor="w")
    log_widget = scrolledtext.ScrolledText(left_panel, width=50, height=20, wrap=tk.WORD)
    log_widget.pack(fill=tk.BOTH, expand=True)

    # --- Right Panel for Plots ---
    right_panel = ttk.Frame(main_frame)
    right_panel.grid(row=0, column=1, sticky="nsew")

    plot_frame = ttk.Frame(right_panel)
    plot_frame.pack(fill=tk.BOTH, expand=True)

    # Pass the buttons to the run_analysis function for dynamic command updates
    run_button.config(command=lambda: run_analysis(ticker_entry, start_date_entry, end_date_entry, plot_frame, metrics_label, log_widget, save_button))

    root.mainloop()

if __name__ == '__main__':
    create_gui()
