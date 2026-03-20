import pandas as pd
import os

def create_disease_features(df):
    df = df.copy()

    # -----------------------------
    # Normalize features safely
    # -----------------------------
    df["temp_norm"] = (df["temp"] - df["temp"].min()) / (df["temp"].max() - df["temp"].min() + 1e-9)
    df["rain_norm"] = (df["rainfall"] - df["rainfall"].min()) / (df["rainfall"].max() - df["rainfall"].min() + 1e-9)
    df["hum_norm"] = (df["humidity"] - df["humidity"].min()) / (df["humidity"].max() - df["humidity"].min() + 1e-9)

    # -----------------------------
    # Create outbreak score
    # -----------------------------
    df["outbreak_score"] = (
        0.5 * df["rain_norm"] +
        0.3 * df["hum_norm"] +
        0.2 * df["temp_norm"]
    )

    # -----------------------------
    # FORCE OUTBREAK LABELS (Top 30%)
    # -----------------------------
    df = df.sort_values(by="outbreak_score", ascending=False)

    top_n = int(0.30 * len(df))  # top 30%
    df["outbreak"] = 0
    df.iloc[:top_n, df.columns.get_loc("outbreak")] = 1

    # Shuffle back to original order
    df = df.sort_index()

    # -----------------------------
    # Debug prints
    # -----------------------------
    print("\nOutbreak distribution:")
    print(df["outbreak"].value_counts())

    print("\nScore stats:")
    print(df["outbreak_score"].describe())

    return df


def save_processed_data(df, filename):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base_dir, "data", "processed", filename)

    os.makedirs(os.path.dirname(path), exist_ok=True)

    df.to_csv(path, index=False)
    print(f"\n✅ Saved to {path}")


if __name__ == "__main__":
    print("Generating disease features...")

    base_dir = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(base_dir, "data", "raw", "weather_data_all_cities.csv")

    df = pd.read_csv(file_path)
    df["date"] = pd.to_datetime(df["date"])

    df = create_disease_features(df)

    print("\nSample data:")
    print(df[["date", "city", "outbreak_score", "outbreak"]].head())

    save_processed_data(df, "weather_with_disease.csv")