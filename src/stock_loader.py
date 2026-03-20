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

        df.reset_index(inplace=True)
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