import pandas as pd
import numpy as np
import os
import json
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier

# Paths
DATA_PATH = "backend/data/climate_stock_extended.csv"
MODEL_PATH = "backend/data/model.pkl"
META_PATH = "backend/data/model_meta.json"

# Load dataset
df = pd.read_csv(DATA_PATH)

# -------------------------------
# 1. Filter valid years (2002–2014)
# -------------------------------
df = df[(df["YEAR"] >= 2002) & (df["YEAR"] <= 2014)]

# -------------------------------
# 2. Sort properly
# -------------------------------
df = df.sort_values(by=["YEAR", "Q_NUM"]).reset_index(drop=True)

# -------------------------------
# 3. Stocks list
# -------------------------------
stocks = [
    "APOLLOHOSP", "AUROPHARMA", "CIPLA",
    "DRREDDY", "LUPIN", "SUNPHARMA"
]

# -------------------------------
# 4. Convert WIDE → LONG format
# -------------------------------
rows = []

for stock in stocks:
    price_col = f"{stock}_PRICE"

    temp = df[["YEAR", "Q_NUM", "R", "T", "H", price_col]].copy()
    temp.rename(columns={price_col: "PRICE"}, inplace=True)
    temp["STOCK"] = stock

    rows.append(temp)

long_df = pd.concat(rows).reset_index(drop=True)

# -------------------------------
# 5. Remove invalid prices
# -------------------------------
long_df = long_df[long_df["PRICE"] > 0]

# -------------------------------
# 6. Create TARGET (next quarter)
# -------------------------------
long_df = long_df.sort_values(by=["STOCK", "YEAR", "Q_NUM"])

long_df["NEXT_PRICE"] = long_df.groupby("STOCK")["PRICE"].shift(-1)

long_df["TARGET"] = (long_df["NEXT_PRICE"] > long_df["PRICE"]).astype(int)

# Drop last rows (no next price)
long_df = long_df.dropna(subset=["NEXT_PRICE"])

# -------------------------------
# 7. Feature Engineering
# -------------------------------
long_df["TEMP_HUM"] = long_df["T"] * long_df["H"]
long_df["RAIN_HUM"] = long_df["R"] * long_df["H"]

# -------------------------------
# 8. Encode STOCK
# -------------------------------
encoder = OneHotEncoder(sparse=False)
stock_encoded = encoder.fit_transform(long_df[["STOCK"]])

stock_df = pd.DataFrame(stock_encoded, columns=encoder.get_feature_names_out(["STOCK"]))

# -------------------------------
# 9. Final Features
# -------------------------------
X = pd.concat([
    long_df[["R", "T", "H", "TEMP_HUM", "RAIN_HUM"]].reset_index(drop=True),
    stock_df.reset_index(drop=True)
], axis=1)

y = long_df["TARGET"]

# -------------------------------
# 10. Train-Test Split (time-based)
# -------------------------------
split_index = int(len(X) * 0.8)

X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

# -------------------------------
# 11. Train Model
# -------------------------------
model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# -------------------------------
# 12. Evaluate
# -------------------------------
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"Model Accuracy: {accuracy:.4f}")

# -------------------------------
# 13. Save model + metadata
# -------------------------------
joblib.dump(model, MODEL_PATH)

meta = {
    "accuracy": float(accuracy),
    "features": list(X.columns),
    "stocks": list(encoder.categories_[0])
}

with open(META_PATH, "w") as f:
    json.dump(meta, f, indent=4)

print("Model and metadata saved!")