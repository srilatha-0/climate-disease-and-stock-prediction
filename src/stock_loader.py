import yfinance as yf
import pandas as pd
import os

def fetch_stock_data(start_date="2014-01-01", end_date="2023-12-31"):

    companies = {
        "CIPLA": "CIPLA.NS",
        "DRREDDY": "DRREDDY.NS",
        "SUNPHARMA": "SUNPHARMA.NS",
        "LUPIN": "LUPIN.NS",
        "DIVISLAB": "DIVISLAB.NS"
    }

    all_data = []

    for name, ticker in companies.items():
        print(f"Fetching stock data for {name}...")

        df = yf.download(ticker, start=start_date, end=end_date)

        # 🔥 Fix MultiIndex issue
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.reset_index(inplace=True)

        # 🔥 Ensure column names are clean
        df.columns = [col.strip() for col in df.columns]

        # 🔥 Select only available columns safely
        cols_needed = ["Date", "Open", "High", "Low", "Close"]
        cols_present = [c for c in cols_needed if c in df.columns]

        df = df[cols_present]

        # Rename columns
        df.rename(columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close"
        }, inplace=True)

        # 🔥 Feature Engineering (only if close exists)
        if "close" in df.columns:
            df["return"] = df["close"].pct_change()
            df["ma_7"] = df["close"].rolling(window=7).mean()

        # Remove nulls
        df.dropna(inplace=True)

        # Add company column
        df["company"] = name

        all_data.append(df)

    final_df = pd.concat(all_data, ignore_index=True)

    return final_df


def save_raw_data(df, filename):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base_dir, "data", "raw", filename)

    os.makedirs(os.path.dirname(path), exist_ok=True)

    df.to_csv(path, index=False)
    print(f"✅ Saved to {path}")


if __name__ == "__main__":
    print("Fetching stock data...")

    df = fetch_stock_data()

    print("\n✅ Stock data fetched!")
    print(df.head())
    print("Shape:", df.shape)

    save_raw_data(df, "stock_data.csv")