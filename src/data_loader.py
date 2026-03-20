import requests
import pandas as pd
import os

def fetch_weather_data_multi(start_date="2014-01-01", end_date="2023-12-31"):
    
    cities = {
        "Hyderabad": (17.3850, 78.4867),
        "Delhi": (28.6139, 77.2090),
        "Mumbai": (19.0760, 72.8777),
        "Kolkata": (22.5726, 88.3639),
        "Chennai": (13.0827, 80.2707)
    }

    all_data = []

    for city, (lat, lon) in cities.items():
        print(f"Fetching data for {city}...")

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
        df["city"] = city  # 🔥 important

        all_data.append(df)

    final_df = pd.concat(all_data, ignore_index=True)

    return final_df


def save_raw_data(df, filename):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base_dir, "data", "raw", filename)

    os.makedirs(os.path.dirname(path), exist_ok=True)

    df.to_csv(path, index=False)
    print(f"✅ Saved to {path}")


if __name__ == "__main__":
    print("Fetching weather data for all cities...")

    df = fetch_weather_data_multi()

    print("\n✅ Data fetched successfully!")
    print(df.head())
    print("Shape:", df.shape)

    save_raw_data(df, "weather_data_all_cities.csv")