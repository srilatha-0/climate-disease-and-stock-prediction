import requests
import pandas as pd
import time

# -----------------------------
# Cities & Coordinates
# -----------------------------
CITY_COORDS = {
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Kolkata": (22.5726, 88.3639),
    "Hyderabad": (17.3850, 78.4867),
    "Bengaluru": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707)
}

# -----------------------------
# Years
# -----------------------------
START_YEAR = 2014
END_YEAR = 2023

# -----------------------------
# FIXED API FUNCTION
# -----------------------------
def fetch_weather(lat, lon, start_date, end_date):
    url = (
        "https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}"
        f"&start_date={start_date}&end_date={end_date}"
        "&daily=temperature_2m_mean,precipitation_sum"
        "&timezone=Asia/Kolkata"
    )

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if "daily" not in data:
            return None

        df = pd.DataFrame(data["daily"])
        return df

    except Exception as e:
        print(f"❌ API error: {e}")
        return None


# -----------------------------
# MAIN LOOP
# -----------------------------
weather_results = []

for city, (lat, lon) in CITY_COORDS.items():
    print(f"\n📍 Fetching weather for {city}")
    city_has_data = False

    for year in range(START_YEAR, END_YEAR + 1):
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"

        df_year = fetch_weather(lat, lon, start_date, end_date)

        if df_year is None or df_year.empty:
            print(f"⚠️ No data for {city} in {year}")
            continue

        city_has_data = True
        df_year["city"] = city
        df_year["year"] = year
        weather_results.append(df_year)

        time.sleep(1)

    if not city_has_data:
        print(f"❌ No data at all for {city}")


# -----------------------------
# SAVE
# -----------------------------
if weather_results:
    weather_df = pd.concat(weather_results, ignore_index=True)
    weather_df.to_csv("weather_fixed.csv", index=False)

    print("\n✅ Data saved: weather_fixed.csv")
    print("Cities fetched:", weather_df["city"].unique())
else:
    print("\n❌ No data fetched at all")