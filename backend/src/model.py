import os
import pandas as pd
import numpy as np
from glob import glob
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from xgboost import XGBClassifier

# =========================
# PATHS
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # parent of src
MERGED_PATH = os.path.join(BASE_DIR, "data", "updatethis")  # Merged dengue+climate+stock
STOCK_PATH  = os.path.join(BASE_DIR, "data", "stocks")      # National stock CSVs

# =========================
# STOCK LIST
# =========================
stocks = ["HYPE3.SA", "FLRY3.SA", "RADL3.SA", "AALR3.SA", "ODPV3.SA"]
stock_monthly = {}

# =========================
# STEP 1 — Load stock data
# =========================
for stock in stocks:
    path = os.path.join(STOCK_PATH, f"{stock}.csv")
    if not os.path.exists(path):
        print(f"⚠️ Stock CSV missing: {stock}")
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

print(f"✅ Loaded stock data for {len(stock_monthly)} stocks")

# =========================
# STEP 2 — Load all state datasets (disease + climate)
# =========================
all_states = glob(os.path.join(MERGED_PATH, "*_merged.csv"))
agg_data = []

for file in all_states:
    state_name = os.path.basename(file).replace("_merged.csv","")
    df = pd.read_csv(file)
    df["Date"] = pd.to_datetime(df["Data"], errors="coerce")
    df = df.dropna(subset=["Date"])
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["State"] = state_name

    # Aggregate municipality-level data to state-level mean per month
    feature_cols = [c for c in df.columns if c not in ["Data","Date","Year","Month","State"]]
    df_agg = df.groupby(["State","Year","Month"])[feature_cols].mean().reset_index()

    agg_data.append(df_agg)

df_all = pd.concat(agg_data, ignore_index=True)
print(f"✅ Aggregated to state-level per month: {df_all.shape}")

# =========================
# STEP 3 — Merge stock returns
# =========================
for stock, sdf in stock_monthly.items():
    df_all = df_all.merge(sdf, on=["Year","Month"], how="left")

# =========================
# STEP 4 — Create lag features
# =========================
LAGS = 3
for stock in stocks:
    col = f"Return_{stock}"
    if col in df_all.columns:
        for lag in range(1,LAGS+1):
            df_all[f"{col}_lag{lag}"] = df_all.groupby("State")[col].shift(lag)

# =========================
# STEP 5 — Create classification target (UP/DOWN)
# =========================
TARGET_STOCK = "HYPE3.SA"
target_col = f"Return_{TARGET_STOCK}"
df_all["Target"] = (df_all.groupby("State")[target_col].shift(-1) > 0).astype(int)

# Drop rows with NaNs (from lag/target)
df_all = df_all.dropna()
print(f"✅ Final dataset shape after lag/target: {df_all.shape}")

# =========================
# STEP 6 — Features and target
# =========================
exclude_cols = ["State","Target"]
feature_cols = [c for c in df_all.columns if c not in exclude_cols]
X = df_all[feature_cols]
y = df_all["Target"]

# Train: 2017-2020, Test: 2021
train_idx = df_all["Year"] <= 2020
test_idx  = df_all["Year"] == 2021

X_train, X_test = X[train_idx], X[test_idx]
y_train, y_test = y[train_idx], y[test_idx]

# =========================
# STEP 7 — Normalize features (optional for tree-based models)
# =========================
# XGBoost does not require normalization, but MinMaxScaler can be used if you want
# scaler = MinMaxScaler()
# X_train = scaler.fit_transform(X_train)
# X_test = scaler.transform(X_test)

# =========================
# STEP 8 — Train XGBoost Classifier
# =========================
model = XGBClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=3,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=(len(y_train)-y_train.sum())/y_train.sum(),
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'
)

model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# =========================
# STEP 9 — Evaluate
# =========================
acc = accuracy_score(y_test, y_pred)
cm  = confusion_matrix(y_test, y_pred)
report = classification_report(y_test, y_pred)

print("\n===== XGBoost Stock UP/DOWN Classification =====")
print(f"Accuracy       : {acc:.4f}")
print(f"Confusion Matrix:\n{cm}")
print(f"Classification Report:\n{report}")