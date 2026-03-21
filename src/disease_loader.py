import pandas as pd
import os

# -----------------------------
# REGION -> CITIES mapping
# -----------------------------
REGION_CITY_MAP = {
    "North": ["Delhi", "Chandigarh", "Jaipur"],
    "South": ["Bengaluru", "Hyderabad", "Chennai", "Kochi"],
    "West": ["Mumbai", "Ahmedabad", "Pune"],
    "East": ["Kolkata", "Bhubaneswar", "Patna"],
    "Northeast": ["Guwahati", "Shillong", "Imphal"],
    "Central": ["Bhopal", "Raipur"],
    "Northwest": ["Jammu", "Shimla"],
    "Southeast": ["Visakhapatnam", "Thiruvananthapuram"]
}

# -----------------------------
# FUNCTION: Process weather
# -----------------------------
def process_weather(weather_df):
    df = weather_df.copy()
    
    # Keep only cities in REGION_CITY_MAP
    valid_cities = [c for cities in REGION_CITY_MAP.values() for c in cities]
    df = df[df["city"].isin(valid_cities)].copy()
    
    # Map city -> region
    city_to_region = {city: region for region, cities in REGION_CITY_MAP.items() for city in cities}
    df["region"] = df["city"].map(city_to_region)
    
    # Convert date
    df["date"] = pd.to_datetime(df["date"])
    
    # Average weather per region per date
    region_weather = df.groupby(["region", "date"])[["temp", "rainfall", "humidity"]].mean().reset_index()
    
    # -----------------------------
    # Normalize climate features
    # -----------------------------
    for col in ["temp", "rainfall", "humidity"]:
        region_weather[f"{col}_norm"] = (region_weather[col] - region_weather[col].min()) / (
            region_weather[col].max() - region_weather[col].min()
        )
    
    # -----------------------------
    # Optional: Compute outbreak score for weather only
    # -----------------------------
    region_weather["outbreak_score"] = (
        0.4 * region_weather["rainfall_norm"] +
        0.3 * region_weather["humidity_norm"] +
        0.3 * region_weather["temp_norm"]
    )
    
    # -----------------------------
    # Adaptive threshold (top 25% = high-risk weather)
    # -----------------------------
    threshold = region_weather["outbreak_score"].quantile(0.75)
    region_weather["high_risk_weather"] = (region_weather["outbreak_score"] > threshold).astype(int)
    
    print("\nWeather threshold used:", threshold)
    print("\nHigh-risk weather distribution:")
    print(region_weather["high_risk_weather"].value_counts())
    
    return region_weather

# -----------------------------
# FUNCTION: Save processed weather
# -----------------------------
def save_processed_weather(df, filename="processed_weather.csv"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "data", "processed", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"\n✅ Processed weather saved to {path}")

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    print("Processing weather data...")
    
    weather_file = os.path.join("data", "raw", "weather_data_all_cities.csv")
    df_weather = pd.read_csv(weather_file)
    
    df_processed = process_weather(df_weather)
    
    print("\nSample processed weather data:")
    print(df_processed.head())
    
    save_processed_weather(df_processed, "weather_data_processed.csv")