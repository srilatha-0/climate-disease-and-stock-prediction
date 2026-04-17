import os
import pandas as pd
import numpy as np

from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# =========================
# PATHS
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

climate_path = os.path.join(BASE_DIR, "data", "final_quarterly_dataset.csv")
stock_path = os.path.join(BASE_DIR, "data", "stock_quarterly_dataset.csv")

# =========================
# LOAD DATA
# =========================
climate = pd.read_csv(climate_path)
stock = pd.read_csv(stock_path)

climate.columns = climate.columns.str.upper().str.strip()
stock.columns = stock.columns.str.upper().str.strip()

# =========================
# CLEAN QUARTER
# =========================
def fix_q(q):
    if pd.isna(q):
        return np.nan
    q = str(q).upper().strip()
    if q in ["1", "1.0", "Q1"]: return "Q1"
    if q in ["2", "2.0", "Q2"]: return "Q2"
    if q in ["3", "3.0", "Q3"]: return "Q3"
    if q in ["4", "4.0", "Q4"]: return "Q4"
    return np.nan

climate["QUARTER"] = climate["QUARTER"].apply(fix_q)
stock["QUARTER"] = stock["QUARTER"].apply(fix_q)

# =========================
# NUMERIC CLEAN (KEEP NaN)
# =========================
for c in climate.columns:
    if c not in ["YEAR", "QUARTER"]:
        climate[c] = pd.to_numeric(climate[c], errors="coerce")

for c in stock.columns:
    if c not in ["YEAR", "QUARTER"]:
        stock[c] = pd.to_numeric(stock[c], errors="coerce")

# =========================
# SORT BEFORE LAGS
# =========================
climate = climate.sort_values(["YEAR", "QUARTER"])
stock = stock.sort_values(["YEAR", "QUARTER"])

# =========================
# MERGE
# =========================
df = pd.merge(climate, stock, on=["YEAR", "QUARTER"], how="outer")
df = df.sort_values(["YEAR", "QUARTER"])

# =========================
# CLIMATE ROLLING FEATURES
# =========================
df["CLIMATE_ROLL3"] = df["CLIMATE_RISK"].rolling(3).mean()
df["RAIN_ROLL3"] = df.get("R_Q3", 0).rolling(3).mean()
df["TEMP_ROLL3"] = df.get("T_Q3", 0).rolling(3).mean()

# =========================
# STOCK FEATURES (FOR EACH STOCK)
# =========================
stock_cols = [c for c in stock.columns if c not in ["YEAR", "QUARTER"]]

for col in stock_cols:
    df[f"{col}_LAG1"] = df[col].shift(1)
    df[f"{col}_LAG2"] = df[col].shift(2)
    df[f"{col}_ROLL3"] = df[col].rolling(3).mean()
    df[f"{col}_RETURN"] = df[col].pct_change()

# =========================
# QUARTER ENCODING
# =========================
df["Q1"] = (df["QUARTER"] == "Q1").astype(int)
df["Q2"] = (df["QUARTER"] == "Q2").astype(int)
df["Q3"] = (df["QUARTER"] == "Q3").astype(int)
df["Q4"] = (df["QUARTER"] == "Q4").astype(int)

# =========================
# DROP INITIAL NANs FROM LAGS
# =========================
df = df.dropna().reset_index(drop=True)

# =========================
# FEATURES (FINAL)
# =========================
base_features = [
    "CLIMATE_RISK",
    "CLIMATE_ROLL3",
    "RAIN_ROLL3",
    "TEMP_ROLL3",
    "Q1", "Q2", "Q3", "Q4"
]

# =========================
# TRAIN MODELS PER STOCK
# =========================
results = {}

for target in stock_cols:

    if target not in df.columns:
        continue

    if df[target].sum() == 0:
        continue

    features = base_features + [
        f"{target}_LAG1",
        f"{target}_LAG2",
        f"{target}_ROLL3",
        f"{target}_RETURN"
    ]

    X = df[features]
    y = df[target]

    # TIME SPLIT (VERY IMPORTANT)
    split = int(len(df) * 0.8)

    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    model = XGBRegressor(
        n_estimators=400,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror"
    )

    model.fit(X_train, y_train)

    pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, pred)
    r2 = r2_score(y_test, pred)

    results[target] = {"MAE": mae, "R2": r2}

    print(f"\n📊 {target}")
    print("MAE:", mae)
    print("R2 :", r2)

# =========================
# SUMMARY
# =========================
print("\n🔥 FINAL MODEL SUMMARY")
for k, v in results.items():
    print(k, "=>", v)