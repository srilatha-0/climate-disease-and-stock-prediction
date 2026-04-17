from fastapi import FastAPI
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROUTES_DIR = os.path.join(BASE_DIR, "routes")

sys.path.append(ROUTES_DIR)

import metrics
import prediction

app = FastAPI(title="Stock API")

@app.get("/")
def home():
    return {"status": "running"}

@app.get("/metrics")
def get_metrics():
    return metrics.get_metrics()

@app.post("/predict/{stock}")
def predict(stock: str):
    return prediction.predict_stock(stock)