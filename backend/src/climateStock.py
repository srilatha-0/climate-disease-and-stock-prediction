import pandas as pd
import numpy as np
import os
import json
import joblib

from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.ensemble import RandomForestClassifier

# -------------------------------
# Paths (UNCHANGED)
# -------------------------------
DATA_PATH = "../data/climate_stock_extended.csv"
MODEL_DIR = "../data/models"
META_PATH = "../data/model_meta.json"
ACCURACY_PATH = "../data/accuracy_metrics.json"

os.makedirs(MODEL_DIR, exist_ok=True)

# -------------------------------
# Load dataset
# -------------------------------
df = pd.read_csv(DATA_PATH)

df = df[(df["YEAR"] >= 2002) & (df["YEAR"] <= 2014)]
df = df.sort_values(by=["YEAR", "Q_NUM"]).reset_index(drop=True)

# -------------------------------
# Stocks
# -------------------------------
stocks = [
    "APOLLOHOSP", "AUROPHARMA", "CIPLA",
    "DRREDDY", "LUPIN", "SUNPHARMA"
]

metrics = {}

# -------------------------------
# Train per stock
# -------------------------------
for stock in stocks:

    print(f"\nTraining {stock}...")

    price_col = f"{stock}_PRICE"

    temp = df[["YEAR", "Q_NUM", "R", "T", "H", price_col]].copy()
    temp.rename(columns={price_col: "PRICE"}, inplace=True)

    # Remove invalid prices
    temp = temp[temp["PRICE"] > 0]

    # Sort
    temp = temp.sort_values(by=["YEAR", "Q_NUM"])

    # -------------------------------
    # SIMPLE + EFFECTIVE LAG
    # -------------------------------
    temp["PRICE_LAG1"] = temp["PRICE"].shift(1)

    # Target
    temp["NEXT_PRICE"] = temp["PRICE"].shift(-1)
    temp["TARGET"] = (temp["NEXT_PRICE"] > temp["PRICE"]).astype(int)

    # Drop NaNs (only 1 row lost now)
    temp = temp.dropna()

    # -------------------------------
    # Feature Engineering
    # -------------------------------
    temp["TEMP_HUM"] = temp["T"] * temp["H"]
    temp["RAIN_HUM"] = temp["R"] * temp["H"]

    X = temp[
        ["R", "T", "H", "TEMP_HUM", "RAIN_HUM", "PRICE_LAG1"]
    ]

    y = temp["TARGET"]

    # -------------------------------
    # Split (time-based)
    # -------------------------------
    split = int(len(X) * 0.8)

    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    # -------------------------------
    # Model (balanced)
    # -------------------------------
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(X_train, y_train)

    # -------------------------------
    # Evaluate
    # -------------------------------
    y_pred = model.predict(X_test)

    if len(y_test) > 0:
        acc = accuracy_score(y_test, y_pred)
        cm = confusion_matrix(y_test, y_pred).tolist()

        metrics[stock] = {
            "accuracy": round(float(acc), 4),
            "confusion_matrix": cm
        }

        print("Accuracy:", acc)
        print("Confusion Matrix:", cm)

    else:
        metrics[stock] = {
            "accuracy": None,
            "confusion_matrix": None
        }

    # -------------------------------
    # Save model (UNCHANGED STRUCTURE)
    # -------------------------------
    model_path = os.path.join(MODEL_DIR, f"model_{stock}.pkl")
    joblib.dump(model, model_path)

    print(f"{stock} model saved!")

# -------------------------------
# Save metrics
# -------------------------------
with open(ACCURACY_PATH, "w") as f:
    json.dump(metrics, f, indent=4)

# -------------------------------
# Save metadata
# -------------------------------
meta = {
    "features": [
        "R", "T", "H",
        "TEMP_HUM", "RAIN_HUM",
        "PRICE_LAG1"
    ],
    "stocks": stocks
}

with open(META_PATH, "w") as f:
    json.dump(meta, f, indent=4)

print("\n✅ FINAL STABLE MODEL BUILT!")