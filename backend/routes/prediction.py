import pickle
import os
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")

PRICE_MODEL_PATH = os.path.join(SRC_DIR, "price_models.pkl")
VOL_MODEL_PATH = os.path.join(SRC_DIR, "vol_models.pkl")

with open(PRICE_MODEL_PATH, "rb") as f:
    price_models = pickle.load(f)

with open(VOL_MODEL_PATH, "rb") as f:
    vol_models = pickle.load(f)


def predict_stock(stock_name: str, features: list):

    model = price_models.get(stock_name) or vol_models.get(stock_name)

    if model is None:
        return {"error": "model not found"}

    X = np.array(features).reshape(1, -1)

    # safety check
    if X.shape[1] != model.n_features_in_:
        return {
            "error": f"Expected {model.n_features_in_} features, got {X.shape[1]}"
        }

    pred_prob = model.predict_proba(X)[0][1]
    pred = int(pred_prob > 0.5)

    return {
        "stock": stock_name,
        "prediction": "UP" if pred == 1 else "DOWN",
        "probability": float(pred_prob)
    }