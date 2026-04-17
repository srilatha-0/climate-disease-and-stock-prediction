import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

# =========================
# PATHS
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

climate_path = os.path.join(DATA_DIR, "final_quarterly_dataset.csv")
stock_path = os.path.join(DATA_DIR, "stock_quarterly_dataset.csv")

# =========================
# LOAD DATA
# =========================
climate = pd.read_csv(climate_path)
stock = pd.read_csv(stock_path)

# =========================
# CLEAN
# =========================
climate.columns = climate.columns.str.strip().str.upper()
stock.columns = stock.columns.str.strip().str.upper()

def fix_quarter(q):
    if pd.isna(q):
        return np.nan
    q = str(q).strip().upper()
    if q in ["1","1.0","Q1"]: return "Q1"
    if q in ["2","2.0","Q2"]: return "Q2"
    if q in ["3","3.0","Q3"]: return "Q3"
    if q in ["4","4.0","Q4"]: return "Q4"
    return np.nan

climate["QUARTER"] = climate["QUARTER"].apply(fix_quarter)
stock["QUARTER"] = stock["QUARTER"].apply(fix_quarter)

# =========================
# NUMERIC CONVERSION
# =========================
for c in climate.columns:
    if c not in ["YEAR","QUARTER"]:
        climate[c] = pd.to_numeric(climate[c], errors="coerce")

for c in stock.columns:
    if c not in ["YEAR","QUARTER"]:
        stock[c] = pd.to_numeric(stock[c], errors="coerce")

# =========================
# QUARTER TO NUMBER
# =========================
q_map = {"Q1":1,"Q2":2,"Q3":3,"Q4":4}
climate["Q_NUM"] = climate["QUARTER"].map(q_map)

# =========================
# TRAIN DATA (1901–2014 ONLY)
# =========================
train = climate[climate["YEAR"] <= 2014].copy()

# FEATURES FOR TIME
train["TIME"] = train["YEAR"] * 4 + train["Q_NUM"]

# =========================
# MODEL INPUTS
# =========================
features = ["TIME"]

targets = [c for c in climate.columns if c not in ["YEAR","QUARTER","Q_NUM","TIME"]]

# =========================
# TRAIN MODELS FOR EACH CLIMATE COLUMN
# =========================
models = {}

for t in targets:
    temp = train[[t, "TIME"]].dropna()

    if len(temp) < 10:
        continue

    X = temp[["TIME"]]
    y = temp[t]

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42
    )

    model.fit(X, y)
    models[t] = model

# =========================
# CREATE FUTURE DATA (2015–2026)
# =========================
future = []

for year in range(2015, 2027):
    for q in [1,2,3,4]:
        future.append({
            "YEAR": year,
            "QUARTER": f"Q{q}",
            "Q_NUM": q,
            "TIME": year * 4 + q
        })

future = pd.DataFrame(future)

# =========================
# PREDICT CLIMATE VALUES
# =========================
for col, model in models.items():
    future[col] = model.predict(future[["TIME"]])

# =========================
# COMBINE CLIMATE
# =========================
climate_full = pd.concat([climate, future], ignore_index=True)

# =========================
# MERGE WITH STOCK
# =========================
df = pd.merge(
    climate_full,
    stock,
    on=["YEAR","QUARTER"],
    how="outer"
)

df = df.sort_values(["YEAR","Q_NUM"])

# =========================
# FILL ONLY STOCK MISSING
# =========================
stock_cols = [c for c in stock.columns if c not in ["YEAR","QUARTER"]]
df[stock_cols] = df[stock_cols].fillna(0)

# =========================
# SAVE FINAL DATASET
# =========================
output_path = os.path.join(DATA_DIR, "climate_stock_extended.csv")
df.to_csv(output_path, index=False)

print("✅ CLIMATE PATTERN LEARNED + EXTENDED")
print("Saved at:", output_path)
print(df.head(10))