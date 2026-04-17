import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")

PRICE_METRICS = os.path.join(SRC_DIR, "price_metrics.json")
VOL_METRICS = os.path.join(SRC_DIR, "vol_metrics.json")


def get_metrics():
    with open(PRICE_METRICS, "r") as f:
        price = json.load(f)

    with open(VOL_METRICS, "r") as f:
        vol = json.load(f)

    return {
        "price_metrics": price,
        "vol_metrics": vol
    }