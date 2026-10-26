"""
Bryan Neil Teddy Semester Project
Getting stock prices from API
Jan. 21 - Apr. 4, 2025 (available trading dates)
"""

"""
Methods of stock price comparison:
close - open
(high - low) / open
price at start date vs price today
"""

from datetime import datetime
from pathlib import Path
import pandas as pd
import yfinance as yf

def get_stock(ticker):
    """
    :param ticker: str. name of stock ticker
    :return: DataFrame, stock prices from Jan. 20 up to Apr. 6, 2025 (exclusive)
    """
    data = yf.download(ticker, start = datetime(2025, 1, 20), end = datetime(2025, 4, 6), auto_adjust=False)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

def price_analysis(ticker, day):
    """
    :param ticker: str. name of stock ticker
    :param day: str. date ("YYYY-MM-DD") of day for prices to be analyzed
    :return: dict. with intraday price change and relative daily range
    """
    data = get_stock(ticker)
    close = float(data.loc[day, "Close"])
    high = float(data.loc[day, "High"])
    low = float(data.loc[day, "Low"])
    opening_price = float(data.loc[day, "Open"])
    metrics = {"Close - Open": close - opening_price, "Day Volatility": (high-low)/opening_price}
    return metrics


if __name__ == "__main__":
    voo = get_stock("VOO")
    voo.to_csv(Path(__file__).resolve().parent / 'stock_data.csv')
    print(voo)
    print(type(voo))
    print(price_analysis("VOO", "2025-03-20"))
