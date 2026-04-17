import os
import yfinance as yf
import pandas as pd

# =========================
# PATH
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
output_path = os.path.join(DATA_DIR, "stock_quarterly_dataset.csv")

# =========================
# UPDATED STOCK LIST (MINIMAL CHANGE)
# =========================
stocks = {
    "CIPLA.NS": "1996-01-01",
    "SUNPHARMA.NS": "1996-01-01",
    "DRREDDY.NS": "1996-01-01",
    "APOLLOHOSP.NS": "2002-01-01",
    "LUPIN.NS": "2000-01-01",
    "AUROPHARMA.NS": "2003-01-01"
}

# =========================
# FUNCTION (same logic)
# =========================
def get_stock_quarterly(ticker, start_date):
    df = yf.download(ticker, start=start_date, progress=False)

    if df is None or df.empty:
        print(f"⚠️ No data for {ticker}")
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if "Close" not in df.columns or "Volume" not in df.columns:
        print(f"⚠️ Missing data for {ticker}")
        return None

    df = df[["Close", "Volume"]].copy()
    df.index = pd.to_datetime(df.index)

    q = df.resample("QE").agg({
        "Close": "mean",
        "Volume": "sum"
    })

    q = q.reset_index()
    q["YEAR"] = q["Date"].dt.year
    q["QUARTER"] = q["Date"].dt.quarter
    q["TICKER"] = ticker

    return q

# =========================
# BUILD DATASET
# =========================
all_data = []

for ticker, start in stocks.items():
    print(f"📥 Downloading {ticker}")
    data = get_stock_quarterly(ticker, start)
    if data is not None:
        all_data.append(data)

final_df = pd.concat(all_data, ignore_index=True)

# =========================
# PIVOT
# =========================
price = final_df.pivot_table(
    index=["YEAR", "QUARTER"],
    columns="TICKER",
    values="Close"
)

volume = final_df.pivot_table(
    index=["YEAR", "QUARTER"],
    columns="TICKER",
    values="Volume"
)

price.columns = [c.replace(".NS", "_PRICE") for c in price.columns]
volume.columns = [c.replace(".NS", "_VOL") for c in volume.columns]

stock_dataset = pd.concat([price, volume], axis=1).reset_index()

# =========================
# SAVE
# =========================
os.makedirs(DATA_DIR, exist_ok=True)
stock_dataset.to_csv(output_path, index=False)

print("✅ DONE")
print("📁 Saved at:", output_path)
print(stock_dataset.head())