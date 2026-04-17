import os
import pandas as pd
import numpy as np
import pickle
import json

from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

# =========================
# LOAD DATA
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "climate_stock_extended.csv")

df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.upper().str.strip()

df = df.apply(pd.to_numeric, errors="coerce")
df = df.ffill().bfill()

# =========================
# QUARTER
# =========================
if "QUARTER" in df.columns:
    df["QUARTER"] = df["QUARTER"].astype(str).str.upper().str.strip()
    df["QUARTER"] = df["QUARTER"].map({"Q1":1, "Q2":2, "Q3":3, "Q4":4})

df["QUARTER"] = df["QUARTER"].fillna(1).astype(int)

# =========================
# FEATURES
# =========================
climate_cols = [c for c in df.columns if c.startswith(("R_", "T_", "H_"))]

df["CLIMATE_MEAN"] = df[climate_cols].mean(axis=1)
df["CLIMATE_STD"] = df[climate_cols].std(axis=1)

df["CLIMATE_L1"] = df["CLIMATE_MEAN"].shift(1)
df["CLIMATE_L2"] = df["CLIMATE_MEAN"].shift(2)
df["CLIMATE_ROLL3"] = df["CLIMATE_MEAN"].rolling(3).mean()

df["Q_SIN"] = np.sin(2*np.pi*df["QUARTER"]/4)
df["Q_COS"] = np.cos(2*np.pi*df["QUARTER"]/4)

df = df.ffill().bfill()

stock_cols = [c for c in df.columns if "PRICE" in c or "VOL" in c]
price_cols = [c for c in stock_cols if "PRICE" in c]
vol_cols = [c for c in stock_cols if "VOL" in c]

base_features = [
    "CLIMATE_MEAN","CLIMATE_STD","CLIMATE_L1",
    "CLIMATE_L2","CLIMATE_ROLL3","Q_SIN","Q_COS"
]

# =========================
# TRAIN FUNCTION
# =========================
def train_models(cols, name):

    models = {}
    metrics = {}

    for target in cols:

        temp = df.copy()

        temp[f"{target}_L1"] = temp[target].shift(1)
        temp[f"{target}_L2"] = temp[target].shift(2)
        temp[f"{target}_ROLL3"] = temp[target].rolling(3).mean()

        temp["TARGET"] = (temp[target].shift(-1) > temp[target]).astype(int)

        features = base_features + [
            f"{target}_L1",
            f"{target}_L2",
            f"{target}_ROLL3"
        ]

        temp = temp[features + ["TARGET"]]
        temp = temp.ffill().bfill()
        temp = temp.iloc[:-1]

        if len(temp) < 50:
            continue

        X = temp[features]
        y = temp["TARGET"]

        split = int(len(temp)*0.8)

        X_train, X_test = X.iloc[:split], X.iloc[split:]
        y_train, y_test = y.iloc[:split], y.iloc[split:]

        model = XGBClassifier(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="binary:logistic"
        )

        model.fit(X_train, y_train)
        pred = model.predict(X_test)

        acc = accuracy_score(y_test, pred)
        prec = precision_score(y_test, pred, zero_division=0)
        rec = recall_score(y_test, pred, zero_division=0)
        f1 = f1_score(y_test, pred, zero_division=0)
        cm = confusion_matrix(y_test, pred).tolist()

        models[target] = model
        metrics[target] = {
            "accuracy": round(acc,3),
            "precision": round(prec,3),
            "recall": round(rec,3),
            "f1": round(f1,3),
            "confusion_matrix": cm
        }

        print(f"{target} -> ACC:{acc:.2f} F1:{f1:.2f}")

    return models, metrics

# =========================
# TRAIN
# =========================
price_models, price_metrics = train_models(price_cols, "PRICE")
vol_models, vol_metrics = train_models(vol_cols, "VOLUME")

# =========================
# SAVE MODELS
# =========================
pickle.dump(price_models, open("price_models.pkl","wb"))
pickle.dump(vol_models, open("vol_models.pkl","wb"))

# =========================
# SAVE METRICS JSON
# =========================
with open("price_metrics.json","w") as f:
    json.dump(price_metrics, f, indent=4)

with open("vol_metrics.json","w") as f:
    json.dump(vol_metrics, f, indent=4)

print("\n✅ TRAINING DONE - CLEAN OUTPUT + FILES SAVED")