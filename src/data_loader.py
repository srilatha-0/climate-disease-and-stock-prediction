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
# STATE -> REGION mapping
# -----------------------------
STATE_REGION_MAP = {
    # North
    "Delhi": "North", "Haryana": "North", "Punjab": "North", "Uttar Pradesh": "North", "Rajasthan": "North",
    # South
    "Karnataka": "South", "Telangana": "South", "Andhra Pradesh": "South", "Tamil Nadu": "South", "Kerala": "South",
    # West
    "Maharashtra": "West", "Gujarat": "West",
    # East
    "West Bengal": "East", "Odisha": "East", "Bihar": "East", "Jharkhand": "East",
    # Northeast
    "Assam": "Northeast", "Arunachal Pradesh": "Northeast", "Nagaland": "Northeast",
    "Manipur": "Northeast", "Mizoram": "Northeast", "Tripura": "Northeast", "Meghalaya": "Northeast", "Sikkim": "Northeast",
    # Central
    "Madhya Pradesh": "Central", "Chhattisgarh": "Central",
    # Northwest
    "Jammu and Kashmir": "Northwest", "Himachal Pradesh": "Northwest",
    # Southeast
    "Andaman and Nicobar Islands": "Southeast", "Puducherry": "Southeast"
}

# -----------------------------
# FUNCTION: Create disease features
# -----------------------------
def create_disease_features(disease_df, weather_df):
    df = disease_df.copy()
    df["region"] = df["state"].map(STATE_REGION_MAP)
    
    # -----------------------------
    # Prepare weather for regions
    # -----------------------------
    # Keep only cities in REGION_CITY_MAP
    weather_df = weather_df[weather_df["city"].isin([c for cities in REGION_CITY_MAP.values() for c in cities])].copy()
    weather_df["date"] = pd.to_datetime(weather_df["date"])
    
    # Map city -> region
    city_to_region = {city: region for region, cities in REGION_CITY_MAP.items() for city in cities}
    weather_df["region"] = weather_df["city"].map(city_to_region)
    
    # Average weather per region per date
    region_weather = weather_df.groupby(["region", "date"])[["temp","rainfall","humidity"]].mean().reset_index()
    
    # Merge region weather with states
    df_merged = df.merge(region_weather, on=["region", "date"], how="left")
    
    # -----------------------------
    # Normalize climate features
    # -----------------------------
    for col in ["temp", "rainfall", "humidity"]:
        df_merged[f"{col}_norm"] = (df_merged[col] - df_merged[col].min()) / (df_merged[col].max() - df_merged[col].min())
    
    # -----------------------------
    # Outbreak score
    # -----------------------------
    df_merged["outbreak_score"] = (
        0.4 * df_merged["rainfall_norm"] +
        0.3 * df_merged["humidity_norm"] +
        0.3 * df_merged["temp_norm"]
    )
    
    # -----------------------------
    # Adaptive threshold (top 25% = outbreak)
    # -----------------------------
    threshold = df_merged["outbreak_score"].quantile(0.75)
    df_merged["outbreak"] = (df_merged["outbreak_score"] > threshold).astype(int)
    
    print("\nThreshold used:", threshold)
    print("\nOutbreak distribution:")
    print(df_merged["outbreak"].value_counts())
    
    return df_merged

# -----------------------------
# FUNCTION: Save processed data
# -----------------------------
def save_processed_data(df, filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "data", "processed", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"\n✅ Saved to {path}")

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    print("Generating disease features...")

    # Load disease data
    disease_file = os.path.join("data", "raw", "disease_yearly_states.csv")
    df_disease = pd.read_csv(disease_file)
    
    # Create dummy date for yearly data (Jan 1 of year)
    df_disease["date"] = pd.to_datetime(df_disease["year"].astype(str) + "-01-01")
    
    # Load weather data
    weather_file = os.path.join("data", "raw", "weather_data_all_cities.csv")
    df_weather = pd.read_csv(weather_file)
    
    # Generate disease features
    df_final = create_disease_features(df_disease, df_weather)
    
    # Show sample
    print("\nSample data:")
    print(df_final[["state", "region", "date", "outbreak_score", "outbreak"]].head())
    
    # Save processed file
    save_processed_data(df_final, "state_weather_with_disease.csv")