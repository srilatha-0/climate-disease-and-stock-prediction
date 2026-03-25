import os
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# =========================
# Paths for your project
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed")  # dengue CSVs
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(OUTPUT_PATH, exist_ok=True)

# =========================
# Load dengue spike CSV
# =========================
spike_df = pd.read_csv(os.path.join(DATA_PATH, "dengue_spike_months.csv"), index_col=0)

# Convert month strings to lists
# =========================
# parsing of spike months
# =========================
def parse_months(val):
    if pd.isna(val) or val == "-":
        return []
    # Convert each element to float first, then int
    return [int(float(x)) for x in str(val).split(",")]

# Apply per column
parsed_spike = spike_df.copy()
for col in spike_df.columns:
    if col not in ["state_peak_month"]:  # ignore non-year columns
        parsed_spike[col] = spike_df[col].apply(parse_months)

# =========================
# Prepare national monthly dengue signal
# =========================
years = [2017,2018,2019,2020,2021]
months = range(1,13)
dengue_signal = []

for year in years:
    for month in months:
        count = 0
        for state in parsed_spike.index:
            if month in parsed_spike.loc[state, str(year)]:
                count += 1
        dengue_signal.append({
            "Year": year,
            "Month": month,
            "Outbreak_Count": count,
            "Dengue_Spike_Binary": 1 if count>0 else 0
        })

dengue_df = pd.DataFrame(dengue_signal)

# =========================
# Fetch Brazilian pharma stock data
# =========================
tickers = ["CBAV3.SA", "RDOR3.SA", "HAPV3.SA", "QUAL3.SA", "CRFB3.SA"]
start_date = "2017-01-01"
end_date = "2021-12-31"

stock_data = {}
for t in tickers:
    df = yf.download(t, start=start_date, end=end_date, interval="1mo")
    df = df.reset_index()[["Date","Close"]]
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Monthly_Return"] = df["Close"].pct_change()
    stock_data[t] = df[["Year","Month","Monthly_Return"]]

# Merge all stocks
stocks_df = stock_data[tickers[0]].copy().rename(columns={"Monthly_Return": tickers[0]})
for t in tickers[1:]:
    stocks_df = stocks_df.merge(stock_data[t], on=["Year","Month"], how="outer")
    stocks_df = stocks_df.rename(columns={"Monthly_Return": t})

# =========================
# Merge dengue spike with stocks
# =========================
merged_df = pd.merge(stocks_df, dengue_df, on=["Year","Month"], how="left")

# =========================
# Correlation analysis
# =========================
print("📊 Correlation of stocks with dengue spikes:")
for t in tickers:
    corr = merged_df[t].corr(merged_df["Dengue_Spike_Binary"])
    print(f"{t}: {corr:.3f}")

# =========================
# Plot stock vs dengue spikes
# =========================
for t in tickers:
    plt.figure(figsize=(12,4))
    plt.plot(merged_df["Year"].astype(str)+"-"+merged_df["Month"].astype(str), merged_df[t], label=t)
    plt.scatter(
        merged_df[merged_df["Dengue_Spike_Binary"]==1]["Year"].astype(str)+"-"+merged_df[merged_df["Dengue_Spike_Binary"]==1]["Month"].astype(str),
        merged_df[merged_df["Dengue_Spike_Binary"]==1][t],
        color="red", label="Dengue Spike"
    )
    plt.xticks(rotation=90)
    plt.title(f"{t} vs Dengue Spike Months")
    plt.legend()
    plt.show()

# =========================
# Save merged CSV (optional)
# =========================
merged_df.to_csv(os.path.join(OUTPUT_PATH, "stocks_dengue_merged.csv"), index=False)
print("🎉 Merged stock+dengue CSV saved!")