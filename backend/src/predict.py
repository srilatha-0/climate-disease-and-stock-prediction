import os
import pandas as pd
import numpy as np

from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import pickle

# =========================
# LOAD DATA
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "climate_stock_extended.csv")

df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.upper().str.strip()

print("\n📊 DATA:", df.shape)

# =========================
# SAFE CLEANING
# =========================
df = df.apply(pd.to_numeric, errors="coerce")
df = df.ffill().bfill()

# =========================
# QUARTER FIX
# =========================
if "QUARTER" in df.columns:
    df["QUARTER"] = df["QUARTER"].astype(str).str.upper().str.strip()

    df["QUARTER"] = df["QUARTER"].map({
        "Q1": 1,
        "Q2": 2,
        "Q3": 3,
        "Q4": 4
    })

df["QUARTER"] = df["QUARTER"].fillna(1).astype(int)

# =========================
# CLIMATE FEATURES
# =========================
climate_cols = [c for c in df.columns if c.startswith(("R_", "T_", "H_"))]

df["CLIMATE_MEAN"] = df[climate_cols].mean(axis=1)
df["CLIMATE_STD"] = df[climate_cols].std(axis=1)

df["CLIMATE_L1"] = df["CLIMATE_MEAN"].shift(1)
df["CLIMATE_L2"] = df["CLIMATE_MEAN"].shift(2)
df["CLIMATE_ROLL3"] = df["CLIMATE_MEAN"].rolling(3).mean()

# =========================
# SEASONAL FEATURES
# =========================
df["Q_SIN"] = np.sin(2 * np.pi * df["QUARTER"] / 4)
df["Q_COS"] = np.cos(2 * np.pi * df["QUARTER"] / 4)

df = df.ffill().bfill()

print("\n📊 FINAL DATA SHAPE:", df.shape)

# =========================
# STOCK COLUMNS
# =========================
stock_cols = [c for c in df.columns if "PRICE" in c or "VOL" in c]

price_cols = [c for c in stock_cols if "PRICE" in c]
vol_cols = [c for c in stock_cols if "VOL" in c]

print("\n📊 PRICE MODELS:", price_cols)
print("📊 VOL MODELS:", vol_cols)

# =========================
# BASE FEATURES
# =========================
base_features = [
    "CLIMATE_MEAN",
    "CLIMATE_STD",
    "CLIMATE_L1",
    "CLIMATE_L2",
    "CLIMATE_ROLL3",
    "Q_SIN",
    "Q_COS"
]

# =========================
# TRAIN FUNCTION (FIXED)
# =========================
def train_models(target_list, name):

    print(f"\n🚀 TRAINING {name} MODELS...\n")

    results = {}

    for target in target_list:

        if target not in df.columns:
            print(f"⚠️ Missing: {target}")
            continue

        temp = df.copy()

        # lag features
        temp[f"{target}_L1"] = temp[target].shift(1)
        temp[f"{target}_L2"] = temp[target].shift(2)
        temp[f"{target}_ROLL3"] = temp[target].rolling(3).mean()

        features = base_features + [
            f"{target}_L1",
            f"{target}_L2",
            f"{target}_ROLL3"
        ]

        temp = temp[features + [target]]

        # drop target NaN only
        temp = temp.dropna(subset=[target])

        # FIX: fill remaining NaNs properly
        temp = temp.ffill().bfill()

        # 🔥 CRITICAL FIX: prevent empty dataset crash
        if len(temp) < 20:
            print(f"⚠️ Skipping {target} (too few rows after cleaning: {len(temp)})")
            continue

        X = temp[features]
        y = temp[target]

        # 🔥 SAFETY CHECK AGAIN
        if X.shape[0] == 0 or y.shape[0] == 0:
            print(f"⚠️ Skipping {target} (empty dataset after processing)")
            continue

        split = max(5, int(len(temp) * 0.8))

        if split >= len(temp):
            print(f"⚠️ Skipping {target} (invalid split)")
            continue

        X_train, X_test = X.iloc[:split], X.iloc[split:]
        y_train, y_test = y.iloc[:split], y.iloc[split:]

        # final safety
        if len(X_train) == 0 or len(X_test) == 0:
            print(f"⚠️ Skipping {target} (train/test empty)")
            continue

        model = XGBRegressor(
            n_estimators=300,
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
        print("MAE:", round(mae, 3))
        print("R2 :", round(r2, 3))

    return results


# =========================
# RUN TRAINING
# =========================
price_results = train_models(price_cols, "PRICE")
vol_results = train_models(vol_cols, "VOLUME")

# =========================
# SAVE MODELS + RESULTS
# =========================
with open("price_results.pkl", "wb") as f:
    pickle.dump(price_results, f)

with open("vol_results.pkl", "wb") as f:
    pickle.dump(vol_results, f)

print("\n🔥 FINAL PRICE RESULTS")
print(price_results)

print("\n🔥 FINAL VOL RESULTS")
print(vol_results)