import pickle
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")

PRICE_MODEL_PATH = os.path.join(SRC_DIR, "price_models.pkl")
VOL_MODEL_PATH = os.path.join(SRC_DIR, "vol_models.pkl")


with open(PRICE_MODEL_PATH, "rb") as f:
    price_models = pickle.load(f)

with open(VOL_MODEL_PATH, "rb") as f:
    vol_models = pickle.load(f)


def predict_stock(stock_name: str):

    model = price_models.get(stock_name) or vol_models.get(stock_name)

    if model is None:
        return {"error": "model not found"}

    # dummy input (replace later with real features)
    import numpy as np
    X = np.random.rand(1, model.n_features_in_)

    pred = model.predict(X)[0]

    return {
        "stock": stock_name,
        "prediction": "UP" if pred == 1 else "DOWN"
    }