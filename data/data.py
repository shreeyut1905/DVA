import yfinance as yf
import pandas as pd
import os

# Specify the folder where CSV files will be saved
folder = "data/2025"

# Create the folder if it doesn't exist
if not os.path.exists(folder):
    os.makedirs(folder)

# Define the tickers and the date range
tickers = ["AAPL", "MSFT", "GOOGL","ABBV","AMZN","TSLA","JNJ","JPM","V","WMT","AMT","BABA","BAC","CSCO","DIS","HD","INTC","KO","MA","NFLX","NKE","NVDA","PEP","PG","PYPL","T","UNH","VZ","XOM"]
start_date = "2020-01-01"
end_date = "2025-1-31"

# Create a dictionary to store cleaned data for each ticker
data_dict = {}



for ticker in tickers:
    # Fetch historical data for the given ticker
    df = yf.download(ticker, start=start_date, end=end_date)
    
    # Remove any rows that contain NaN values
    df_clean = df.dropna()
    
    # Exclude unwanted columns (Dividends and Stock Splits)
    # df_clean = df_clean.drop(columns=["Dividends", "Stock Splits"])
    
    # Add a 'Target' column: Percentage change in 'Close' price for the next day
    df_clean["Target"] = df_clean["Close"].pct_change().shift(-1) * 100
    df_clean = df_clean[:-1]  # Remove last row, which will have NaN in 'Target'
    
    # Ensure the datetime index is uniformly processed.
    # Convert index to datetime in UTC and then remove the timezone information.
    df_clean.index = pd.to_datetime(df_clean.index, utc=True).tz_convert(None)

    # Define the file path in the specified folder and save the DataFrame as CSV
    file_path = os.path.join(folder, f"{ticker}.csv")
    df_clean.to_csv(file_path)

print("OHLCV data has been downloaded, cleaned, and stored in the folder successfully!")