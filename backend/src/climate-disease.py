import os
import pandas as pd
import numpy as np
from tqdm import tqdm
import xgboost as xgb
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder

# =========================
# BASE PATHS
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(
    BASE_DIR,
    "Dengue-Brasil-Arboviroses-Dataset-Brazil-Dengue-Arboviral-Diseases-Dataset",
    "DengueDataset",
    "data"
)
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(OUTPUT_PATH, exist_ok=True)

# =========================
# PARAMETERS
# =========================
LAG_MONTHS = 3          # Lag months for features
TARGET_COL = "Dengue"   # Name of dengue column
TRAIN_YEARS = list(range(1999, 2017))
TEST_YEARS = list(range(2017, 2022))

# =========================
# GET ALL CSV FILES
# =========================
all_files = []
for root, dirs, files in os.walk(DATA_PATH):
    for file in files:
        if file.endswith(".csv"):
            all_files.append(os.path.join(root, file))

total_files = len(all_files)
print(f"\n🚀 Total state files found: {total_files}\n")
if total_files == 0:
    raise FileNotFoundError(f"No CSV files found in {DATA_PATH}!")

# =========================
# HELPER FUNCTIONS
# =========================
def create_lag_features(df, col_list, lag=3):
    """Creates lag features for each column in col_list"""
    for col in col_list:
        for i in range(1, lag+1):
            df[f"{col}_lag{i}"] = df[col].shift(i)
    return df

def encode_month(df):
    """Encode month cyclically to capture seasonality"""
    df["month_sin"] = np.sin(2 * np.pi * df["month"]/12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"]/12)
    return df

# =========================
# PREPARE TRAIN & TEST DATA
# =========================
train_X_list, train_y_list = [], []
test_X_list, test_y_list = [], []

for idx, file_path in enumerate(tqdm(all_files, desc="Processing states")):
    try:
        df = pd.read_csv(file_path, encoding="latin1")
        df.columns = df.columns.str.strip()
        state_name = os.path.basename(file_path).replace(".csv", "")
        df["state"] = state_name

        # Parse date
        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
        df["year"] = df["Data"].dt.year
        df["month"] = df["Data"].dt.month

        # Filter years
        df = df[(df["year"] >= 1999) & (df["year"] <= 2021)].sort_values("Data").reset_index(drop=True)

        # Dengue column
        dengue_cols = [c for c in df.columns if "Dengue" in c]
        if not dengue_cols:
            print(f"⚠️ No dengue column in {state_name}, skipped")
            continue
        dengue_col = dengue_cols[0]

        # Climate columns
        temp_cols = [c for c in df.columns if "Temperatura" in c]
        rain_cols = [c for c in df.columns if "Precip" in c]
        hum_cols = [c for c in df.columns if "Umidade" in c]

        climate_cols = temp_cols + rain_cols + hum_cols

        # Fill missing values
        df[climate_cols] = df[climate_cols].ffill().bfill()
        df[dengue_col] = df[dengue_col].fillna(0)

        # Lag features
        df = create_lag_features(df, [dengue_col] + climate_cols, LAG_MONTHS)
        df = df.dropna().reset_index(drop=True)

        # Month cyclic encoding
        df = encode_month(df)

        # Features and target
        feature_cols = [c for c in df.columns if c not in ["Data", "year", TARGET_COL, "state"]]
        df[TARGET_COL+"_binary"] = (df[dengue_col] > 0).astype(int)

        # Split train/test
        train_df = df[df["year"].isin(TRAIN_YEARS)]
        test_df = df[df["year"].isin(TEST_YEARS)]

        if not train_df.empty:
            train_X_list.append(train_df[feature_cols])
            train_y_list.append(train_df[TARGET_COL+"_binary"])
        if not test_df.empty:
            test_X_list.append(test_df[feature_cols])
            test_y_list.append(test_df[TARGET_COL+"_binary"])

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

# =========================
# CONCAT ALL
# =========================
if not train_X_list or not test_X_list:
    raise ValueError("No train/test data found!")

train_X = pd.concat(train_X_list, ignore_index=True)
train_y = pd.concat(train_y_list, ignore_index=True)
test_X = pd.concat(test_X_list, ignore_index=True)
test_y = pd.concat(test_y_list, ignore_index=True)

print(f"\nTraining samples: {len(train_X)}, Testing samples: {len(test_X)}\n")

# =========================
# HANDLE CATEGORICAL STATE
# =========================
le = LabelEncoder()
train_X["state_enc"] = le.fit_transform(train_X_list[0]["state"]) if "state" in train_X_list[0].columns else 0
test_X["state_enc"] = le.transform(test_X_list[0]["state"]) if "state" in test_X_list[0].columns else 0

# =========================
# CALCULATE SCALE POS WEIGHT
# =========================
neg, pos = np.bincount(train_y)
scale_pos_weight = neg / pos

# =========================
# TRAIN XGBOOST
# =========================
dtrain = xgb.DMatrix(train_X, label=train_y)
dtest = xgb.DMatrix(test_X, label=test_y)

params = {
    "objective": "binary:logistic",
    "eval_metric": "logloss",
    "tree_method": "hist",
    "learning_rate": 0.1,
    "max_depth": 6,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "scale_pos_weight": scale_pos_weight,
    "seed": 42
}

evals = [(dtrain, "train"), (dtest, "eval")]

print("🚀 Training XGBoost model with imbalance handling...")
bst = xgb.train(
    params,
    dtrain,
    num_boost_round=500,
    evals=evals,
    early_stopping_rounds=50,
    verbose_eval=50
)

# =========================
# PREDICTIONS & EVAL
# =========================
pred_probs = bst.predict(dtest)
threshold = 0.3  # tuned threshold for better F1
pred_labels = (pred_probs > threshold).astype(int)

accuracy = accuracy_score(test_y, pred_labels)
f1 = f1_score(test_y, pred_labels)
roc_auc = roc_auc_score(test_y, pred_probs)
cm = confusion_matrix(test_y, pred_labels)

print("\n✅ Evaluation Metrics:")
print(f"Accuracy : {accuracy:.4f}")
print(f"F1 Score : {f1:.4f}")
print(f"ROC AUC  : {roc_auc:.4f}")
print(f"Confusion Matrix:\n{cm}")

