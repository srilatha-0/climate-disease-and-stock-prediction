import os
import pandas as pd

# =========================
# PATH
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

rain_path = os.path.join(DATA_DIR, "rainfall.xls")
temp_path = os.path.join(DATA_DIR, "temperature.csv")

# =========================
# LOAD
# =========================
rain = pd.read_excel(rain_path)
temp = pd.read_csv(temp_path)

# =========================
# CLEAN COLUMN NAMES
# =========================
rain.columns = rain.columns.str.strip()
temp.columns = temp.columns.str.strip()

rain = rain.fillna(0)
temp = temp.fillna(0)

# convert safely
for col in rain.columns:
    if col != "YEAR":
        rain[col] = pd.to_numeric(rain[col], errors="coerce").fillna(0)

for col in temp.columns:
    if col != "YEAR":
        temp[col] = pd.to_numeric(temp[col], errors="coerce").fillna(0)

# =========================
# QUARTER DEFINITIONS (AUTO MATCH)
# =========================
q1_cols = [c for c in rain.columns if c in ["JAN", "FEB"]]
q2_cols = [c for c in rain.columns if c in ["MAR", "APR", "MAY"]]
q3_cols = [c for c in rain.columns if c in ["JUN", "JUL", "AUG", "SEP"]]
q4_cols = [c for c in rain.columns if c in ["OCT", "NOV", "DEC"]]

# =========================
# BUILD RAIN QUARTERS
# =========================
rain_q = pd.DataFrame()
rain_q["YEAR"] = rain["YEAR"]

rain_q["R_Q1"] = rain[q1_cols].sum(axis=1)
rain_q["R_Q2"] = rain[q2_cols].sum(axis=1)
rain_q["R_Q3"] = rain[q3_cols].sum(axis=1)
rain_q["R_Q4"] = rain[q4_cols].sum(axis=1)

# =========================
# BUILD TEMP QUARTERS (direct mapping)
# =========================
temp_q = pd.DataFrame()
temp_q["YEAR"] = temp["YEAR"]

temp_q["T_Q1"] = temp[[c for c in temp.columns if "JAN-FEB" in c]].iloc[:, 0]
temp_q["T_Q2"] = temp[[c for c in temp.columns if "MAR-MAY" in c]].iloc[:, 0]
temp_q["T_Q3"] = temp[[c for c in temp.columns if "JUN-SEP" in c]].iloc[:, 0]
temp_q["T_Q4"] = temp[[c for c in temp.columns if "OCT-DEC" in c]].iloc[:, 0]

# =========================
# MERGE
# =========================
df = pd.merge(rain_q, temp_q, on="YEAR")

# =========================
# HUMIDITY (SAFE)
# =========================
eps = 1

for q in ["Q1", "Q2", "Q3", "Q4"]:
    df[f"H_{q}"] = df[f"R_{q}"] / (df[f"T_{q}"] + eps)

# =========================
# SAVE
# =========================
output_path = os.path.join(DATA_DIR, "final_quarterly_dataset.csv")
df.to_csv(output_path, index=False)

print("✅ DONE")
print(df.head())