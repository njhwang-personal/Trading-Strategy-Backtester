import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_data(ticker: str, years: int) -> pd.DataFrame:

    end_date = datetime.today().strftime('%Y-%m-%d')        #today
    start_date = (datetime.today() - timedelta(days = 365 * years)).strftime('%Y-%m-%d')  #10 years ago

    data = yf.download(ticker, start = start_date, end = end_date, auto_adjust = True, interval = "1d", progress = False)
    if(data.empty):
        raise RuntimeError("No data returned for {ticker}")
    
    if "Adj Close" in data.columns:
        data = data.rename(columns={"Adj Close": "Close"})
    data = data[["Close"]].dropna().copy()
    data.index.name = "Date"

    return data