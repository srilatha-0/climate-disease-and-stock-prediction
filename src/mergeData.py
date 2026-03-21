import pandas as pd
import os

def load_data():
    base_dir = os.path.dirname(os.path.dirname(__file__))

    weather_path = os.path.join(base_dir, "data", "processed", "weather_with_disease.csv")
    stock_path = os.path.join(base_dir, "data", "raw", "stock_data.csv")

    weather_df = pd.read_csv(weather_path)
    stock_df = pd.read_csv(stock_path)

    weather_df["date"] = pd.to_datetime(weather_df["date"])
    stock_df["date"] = pd.to_datetime(stock_df["date"])

    return weather_df, stock_df


def merge_data(weather_df, stock_df):
    # Merge on date
    merged_df = pd.merge(weather_df, stock_df, on="date", how="inner")

    return merged_df


def save_data(df, filename):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base_dir, "data", "processed", filename)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)

    print(f"✅ Saved to {path}")


if __name__ == "__main__":
    print("Merging datasets...")

    weather_df, stock_df = load_data()
    merged_df = merge_data(weather_df, stock_df)

    print("\n✅ Merge Done!")
    print(merged_df.head())
    print("Shape:", merged_df.shape)

    save_data(merged_df, "final_merged_data.csv")