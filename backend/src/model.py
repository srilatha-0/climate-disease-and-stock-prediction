import os
import pandas as pd
import numpy as np
from glob import glob
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from xgboost import XGBClassifier
import yfinance as yf
import json
import pickle

# =========================
# PATHS (FIXED)
# =========================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

MERGED_PATH = os.path.join(BASE_DIR, "data", "updatethis")
STOCK_PATH  = os.path.join(BASE_DIR, "data", "stocks")

os.makedirs(STOCK_PATH, exist_ok=True)

print("📁 BASE DIR:", BASE_DIR)
print("📁 STOCK PATH:", STOCK_PATH)

# =========================
# STOCK LIST
# =========================
stocks = ["HYPE3.SA", "FLRY3.SA", "RADL3.SA", "AALR3.SA", "ODPV3.SA"]

# =========================
# STEP 0 — AUTO DOWNLOAD STOCKS
# =========================
print("\n🚀 Checking/downloading stock data...")

for stock in stocks:
    path = os.path.join(STOCK_PATH, f"{stock}.csv")

    if os.path.exists(path):
        print(f"✅ Exists: {stock}")
        continue

    print(f"⬇️ Downloading {stock}...")
    df = yf.download(stock, start="2017-01-01", end="2021-12-31", progress=False)

    if not df.empty:
        df.to_csv(path)
        print(f"✅ Saved: {stock}")
    else:
        print(f"⚠️ Failed: {stock}")

# =========================
# STEP 1 — LOAD STOCK DATA
# =========================
stock_monthly = {}

for stock in stocks:
    path = os.path.join(STOCK_PATH, f"{stock}.csv")

    if not os.path.exists(path):
        print(f"⚠️ Missing stock file: {stock}")
        continue

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    df.rename(columns={df.columns[0]: "Date"}, inplace=True)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    for col in ["Open","High","Low","Close","Adj Close","Volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Close"])

    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month

    monthly = df.groupby(["Year","Month"])["Close"].mean().reset_index()
    monthly["Return"] = monthly["Close"].pct_change().fillna(0)

    monthly = monthly.rename(columns={
        "Close": f"Close_{stock}",
        "Return": f"Return_{stock}"
    })

    stock_monthly[stock] = monthly

print(f"\n✅ Loaded stock data for {len(stock_monthly)} stocks")

if len(stock_monthly) == 0:
    raise Exception("❌ No stock data available even after download!")

# =========================
# STEP 2 — LOAD STATE DATA
# =========================
all_states = glob(os.path.join(MERGED_PATH, "*_merged.csv"))

if len(all_states) == 0:
    raise FileNotFoundError("❌ No merged state files found in data/updatethis")

agg_data = []

for file in all_states:
    state_name = os.path.basename(file).replace("_merged.csv","")

    df = pd.read_csv(file)

    df["Date"] = pd.to_datetime(df["Data"], errors="coerce")
    df = df.dropna(subset=["Date"])

    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["State"] = state_name

    feature_cols = [c for c in df.columns if c not in ["Data","Date","Year","Month","State"]]

    df_agg = df.groupby(["State","Year","Month"])[feature_cols].mean().reset_index()
    agg_data.append(df_agg)

df_all = pd.concat(agg_data, ignore_index=True)
print(f"✅ Aggregated dataset shape: {df_all.shape}")

# =========================
# STEP 3 — MERGE STOCK DATA
# =========================
for stock, sdf in stock_monthly.items():
    df_all = df_all.merge(sdf, on=["Year","Month"], how="left")

# =========================
# STEP 4 — CREATE LAGS
# =========================
LAGS = 3

for stock in stocks:
    col = f"Return_{stock}"
    if col in df_all.columns:
        for lag in range(1, LAGS+1):
            df_all[f"{col}_lag{lag}"] = df_all.groupby("State")[col].shift(lag)

# =========================
# STEP 5 — TARGET (SAFE FIX)
# =========================
TARGET_STOCK = "HYPE3.SA"
target_col = f"Return_{TARGET_STOCK}"

# 🔥 FIX: don't crash → skip if missing
if target_col not in df_all.columns:
    print(f"❌ WARNING: {target_col} not found → skipping model training")
    exit()

df_all["Target"] = (df_all.groupby("State")[target_col].shift(-1) > 0).astype(int)

# Drop NaNs
df_all = df_all.dropna()
print(f"✅ Final dataset shape: {df_all.shape}")

# =========================
# STEP 6 — FEATURES (SAFE FIX)
# =========================
exclude_cols = ["State", "Target"]
feature_cols = [c for c in df_all.columns if c not in exclude_cols]

X = df_all[feature_cols].select_dtypes(include=[np.number])
y = df_all["Target"]

# =========================
# STEP 7 — TRAIN TEST SPLIT
# =========================
train_idx = df_all["Year"] <= 2020
test_idx  = df_all["Year"] == 2021

X_train, X_test = X[train_idx], X[test_idx]
y_train, y_test = y[train_idx], y[test_idx]

# =========================
# STEP 8 — MODEL
# =========================
scale_pos_weight = (len(y_train) - y_train.sum()) / y_train.sum()

model = XGBClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=3,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=scale_pos_weight,
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'
)

print("\n🚀 Training model...")
model.fit(X_train, y_train)

# =========================
# STEP 9 — EVALUATION
# =========================
y_pred = model.predict(X_test)

acc = accuracy_score(y_test, y_pred)
cm  = confusion_matrix(y_test, y_pred)
report = classification_report(y_test, y_pred)

# =========================
# SAVE METRICS (backend/src)
# =========================
SRC_DIR = os.path.dirname(__file__)

metrics = {
    "accuracy": float(acc),
    "confusion_matrix": cm.tolist(),
    "classification_report": report
}

metrics_path = os.path.join(SRC_DIR, "metrics.json")

with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=4)

print(f"📊 Metrics saved at: {metrics_path}")

# =========================
# SAVE MODEL (.pkl)
# =========================
model_path = os.path.join(SRC_DIR, "model.pkl")

with open(model_path, "wb") as f:
    pickle.dump(model, f)

print(f"💾 Model saved at: {model_path}")

print("\n===== FINAL RESULTS =====")
print(f"Accuracy       : {acc:.4f}")
print(f"Confusion Matrix:\n{cm}")
print(f"Classification Report:\n{report}")