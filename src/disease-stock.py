import os
import pandas as pd
import yfinance as yf

# =========================
# PATHS
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

STATE_DATA_PATH = os.path.join(
    BASE_DIR,
    "Dengue-Brasil-Arboviroses-Dataset-Brazil-Dengue-Arboviral-Diseases-Dataset",
    "DengueDataset",
    "data"
)

SPIKE_PATH = os.path.join(BASE_DIR, "data", "processed", "dengue_spike_months.csv")
STOCK_PATH = os.path.join(BASE_DIR, "data", "stocks")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "updatethis")

os.makedirs(STOCK_PATH, exist_ok=True)
os.makedirs(OUTPUT_PATH, exist_ok=True)

# =========================
# STEP 1 — DOWNLOAD STOCKS
# =========================
print("\n🚀 Downloading pharma stocks...")

stocks = ["HYPE3.SA", "FLRY3.SA", "RADL3.SA", "AALR3.SA", "ODPV3.SA"]

for stock in stocks:
    path = os.path.join(STOCK_PATH, f"{stock}.csv")

    if os.path.exists(path):
        print(f"✅ Already exists: {stock}")
        continue

    print(f"⬇️ Downloading {stock}")
    df = yf.download(stock, start="2017-01-01", end="2021-12-31", progress=False)

    if df.empty:
        print(f"⚠️ Skipped {stock}")
        continue

    df.to_csv(path)

# =========================
# STEP 2 — PROCESS STOCK DATA
# =========================
print("\n🚀 Processing stock data...")

stock_monthly = {}

for file in os.listdir(STOCK_PATH):
    if not file.endswith(".csv"):
        continue

    print(f"\n🔄 Processing: {file}")

    try:
        file_path = os.path.join(STOCK_PATH, file)

        df = pd.read_csv(file_path)

        # Clean column names
        df.columns = df.columns.str.strip()

        # Rename first column to Date
        df.rename(columns={df.columns[0]: "Date"}, inplace=True)

        # Remove empty rows
        df = df[df["Date"].notna()]
        df = df[df["Date"] != ""]

        # Convert Date
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["Date"])

        # Convert numeric columns
        for col in ["Close", "Open", "High", "Low", "Volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Ensure Close exists
        if "Close" not in df.columns:
            print("❌ No Close column → skipping")
            continue

        df = df.dropna(subset=["Close"])

        if df.empty:
            print("❌ Empty after cleaning → skipping")
            continue

        print(f"✅ Cleaned rows: {len(df)}")

        # Create monthly
        df["Year"] = df["Date"].dt.year
        df["Month"] = df["Date"].dt.month

        monthly = df.groupby(["Year", "Month"])["Close"].mean().reset_index()
        monthly["Return"] = monthly["Close"].pct_change()
        monthly["Return"] = monthly["Return"].fillna(0)

        stock_name = file.replace(".csv", "")
        stock_monthly[stock_name] = monthly

        print(f"✅ Ready: {stock_name}")

    except Exception as e:
        print(f"❌ Failed {file}: {e}")

print(f"\n📊 Total stocks ready: {len(stock_monthly)}")

# =========================
# LOAD SPIKE DATA
# =========================
spike_df = pd.read_csv(SPIKE_PATH)

# Drop unwanted column
if "state_peak_month" in spike_df.columns:
    spike_df.drop(columns=["state_peak_month"], inplace=True)

# Set index (state name)
spike_df.set_index(spike_df.columns[0], inplace=True)

# Fix column names (2017.0 → 2017)
fixed_cols = []
for col in spike_df.columns:
    try:
        fixed_cols.append(str(int(float(col))))
    except:
        fixed_cols.append(col)

spike_df.columns = fixed_cols

print("✅ Spike columns fixed:", spike_df.columns)

# =========================
# STEP 3 — STATE ANALYSIS + MERGE
# =========================
print("\n🚀 Starting STATE-WISE analysis + merging...")

all_state_files = []

for root, dirs, files in os.walk(STATE_DATA_PATH):
    for file in files:
        if file.endswith(".csv"):
            all_state_files.append(os.path.join(root, file))

print(f"\n📊 Total states: {len(all_state_files)}")

for idx, file_path in enumerate(all_state_files, 1):

    try:
        state_name = os.path.basename(file_path).replace(".csv", "")

        print("\n==============================")
        print(f"🔍 [{idx}] STATE: {state_name}")
        print("==============================")

        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()

        # Date processing
        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
        df = df.dropna(subset=["Data"])

        df = df[(df["Data"].dt.year >= 2017) & (df["Data"].dt.year <= 2021)]

        df["Year"] = df["Data"].dt.year
        df["Month"] = df["Data"].dt.month

        if state_name not in spike_df.index:
            print("⚠️ No spike data → skipping")
            continue

        row = spike_df.loc[state_name]

        selected_stocks = []

        # =========================
        # ANALYSIS
        # =========================
        for stock_name, sdf in stock_monthly.items():

            print(f"\n📈 Analyzing {stock_name}...")

            spike_returns = []
            normal_returns = []

            for year in ["2017","2018","2019","2020","2021"]:

                if year not in row or pd.isna(row[year]):
                    continue

                months = str(row[year]).split(",")

                for m in months:
                    m = int(float(m))

                    val = sdf[(sdf["Year"] == int(year)) & (sdf["Month"] == m)]

                    if not val.empty:
                        spike_returns.append(val["Return"].values[0])

            for _, r in sdf.iterrows():
                if r["Return"] not in spike_returns:
                    normal_returns.append(r["Return"])

            if len(spike_returns) == 0:
                print("⚠️ No spike data")
                continue

            spike_avg = pd.Series(spike_returns).mean()
            normal_avg = pd.Series(normal_returns).mean()

            diff = spike_avg - normal_avg

            if diff > 0.01:
                relation = "UP 📈"
                selected_stocks.append(stock_name)
            elif diff < -0.01:
                relation = "DOWN 📉"
                selected_stocks.append(stock_name)
            else:
                relation = "NORMAL ➖"

            print(f"➡️ {relation} (diff={diff:.4f})")

        print(f"\n✅ Selected stocks: {selected_stocks}")

        # =========================
        # MERGE
        # =========================
        added_cols = []

        for stock in selected_stocks:
            sdf = stock_monthly[stock]

            temp = sdf.rename(columns={
                "Close": f"{stock}_Close",
                "Return": f"{stock}_Return"
            })

            df = pd.merge(df, temp, on=["Year","Month"], how="left")

            added_cols += [f"{stock}_Close", f"{stock}_Return"]

        print(f"📊 Columns added: {added_cols}")

        # =========================
        # CORRELATION FOR ALL STATES + ALL SELECTED STOCKS
        # =========================
        dengue_col = "Taxa de Internações por Dengue"

        if len(selected_stocks) > 0 and dengue_col in df.columns:

            monthly_dengue = df.groupby(["Year","Month"])[dengue_col].mean().reset_index()

            for stock in selected_stocks:
                stock_close_col = f"{stock}_Close"
                stock_data = df.groupby(["Year","Month"])[stock_close_col].mean().reset_index()

                merged_temp = pd.merge(monthly_dengue, stock_data, on=["Year","Month"])
                corr = merged_temp[dengue_col].corr(merged_temp[stock_close_col])

                print(f"📊 [{state_name}] Correlation between dengue and {stock}: {corr:.4f}")

        # SAVE
        out_path = os.path.join(OUTPUT_PATH, f"{state_name}_merged.csv")
        df.to_csv(out_path, index=False)

        print(f"💾 Saved: {state_name}")

    except Exception as e:
        print(f"❌ Error: {e}")

print("\n🎉 DONE — FULL PIPELINE + CORRELATION COMPLETE!")