import pandas as pd
import os

def create_disease_features(df):
    df = df.copy()

    # -----------------------------
    # Normalize features (0–1 scale)
    # -----------------------------
    df["temp_norm"] = (df["temp"] - df["temp"].min()) / (df["temp"].max() - df["temp"].min())
    df["rain_norm"] = (df["rainfall"] - df["rainfall"].min()) / (df["rainfall"].max() - df["rainfall"].min())
    df["hum_norm"] = (df["humidity"] - df["humidity"].min()) / (df["humidity"].max() - df["humidity"].min())

    # -----------------------------
    # Create outbreak score (weighted)
    # -----------------------------
    df["outbreak_score"] = (
        0.4 * df["rain_norm"] +
        0.3 * df["hum_norm"] +
        0.3 * df["temp_norm"]
    )

    # -----------------------------
    # Adaptive Threshold (FIXED)
    # -----------------------------
    threshold = df["outbreak_score"].quantile(0.75)  # top 25% as outbreaks

    df["outbreak"] = (df["outbreak_score"] > threshold).astype(int)

    # Debug prints (VERY IMPORTANT)
    print("\nThreshold used:", threshold)
    print("\nOutbreak distribution:")
    print(df["outbreak"].value_counts())

    return df


def save_processed_data(df, filename):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base_dir, "data", "processed", filename)

    os.makedirs(os.path.dirname(path), exist_ok=True)

    df.to_csv(path, index=False)
    print(f"\n✅ Saved to {path}")


if __name__ == "__main__":
    print("Generating disease features...")

    # Load weather data
    base_dir = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(base_dir, "data", "raw", "weather_data_all_cities.csv")

    df = pd.read_csv(file_path)
    df["date"] = pd.to_datetime(df["date"])

    # Create disease features
    df = create_disease_features(df)

    # Show sample
    print("\nSample data:")
    print(df[["date", "city", "outbreak_score", "outbreak"]].head())

    # Save file
    save_processed_data(df, "weather_with_disease.csv")