import requests
import pandas as pd

def fetch_weather_data(start_date="2014-01-01", end_date="2023-12-31"):
    # Hyderabad coordinates
    lat = 17.3850
    lon = 78.4867

    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=temperature_2m_mean,precipitation_sum,relative_humidity_2m_mean&timezone=Asia%2FKolkata"

    response = requests.get(url)
    data = response.json()

    df = pd.DataFrame({
        "date": data["daily"]["time"],
        "temp": data["daily"]["temperature_2m_mean"],
        "rainfall": data["daily"]["precipitation_sum"],
        "humidity": data["daily"]["relative_humidity_2m_mean"]
    })

    df["date"] = pd.to_datetime(df["date"])
    return df


import os

def save_raw_data(df, filename):
    base_dir = os.path.dirname(os.path.dirname(__file__))

    path = os.path.join(base_dir, "data", "raw", filename)

    os.makedirs(os.path.dirname(path), exist_ok=True)

    df.to_csv(path, index=False)
    print(f"✅ Saved to {path}")

if __name__ == "__main__":
    print("Testing data loader...")

    df = fetch_weather_data()
    print(df.head())
    print("Shape:", df.shape)

    save_raw_data(df, "weather_data.csv")