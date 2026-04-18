import pandas as pd
import joblib
import json

MODEL_DIR = "../data/models"
META_PATH = "../data/model_meta.json"

with open(META_PATH, "r") as f:
    meta = json.load(f)

features = meta["features"]

# -------------------------------
# USER INPUT
# -------------------------------
input_data = {
    "R": 200,
    "T": 30,
    "H": 20,
    "STOCK": "CIPLA",
    "LAST_PRICE": 950   # only 1 value needed now
}

# Load correct model
stock = input_data["STOCK"]
model = joblib.load(f"{MODEL_DIR}/model_{stock}.pkl")

# Feature engineering
input_data["PRICE_LAG1"] = input_data["LAST_PRICE"]
input_data["TEMP_HUM"] = input_data["T"] * input_data["H"]
input_data["RAIN_HUM"] = input_data["R"] * input_data["H"]

# Remove unused
input_data.pop("STOCK")
input_data.pop("LAST_PRICE")

# DataFrame
df = pd.DataFrame([input_data])
df = df[features]

# Prediction
prediction = model.predict(df)[0]
prob = model.predict_proba(df)[0][1]

print("Prediction (1 = Increase):", prediction)
print("Confidence:", round(prob, 3))