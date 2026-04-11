import os
import pandas as pd

# =========================
# BASE PROJECT PATH (CDH)
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "Dengue-Brasil-Arboviroses-Dataset-Brazil-Dengue-Arboviral-Diseases-Dataset",
    "DengueDataset",
    "data"
)

OUTPUT_PATH = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(OUTPUT_PATH, exist_ok=True)

# =========================
# GET ALL CSV FILES
# =========================
all_files = []
for root, dirs, files in os.walk(DATA_PATH):
    for file in files:
        if file.endswith(".csv"):
            all_files.append(os.path.join(root, file))

total_files = len(all_files)
print(f"\n🚀 Total state files found: {total_files}\n")
if total_files == 0:
    raise FileNotFoundError(f"No CSV files found in {DATA_PATH}!")

# =========================
# STORE RESULTS
# =========================
climate_result = []
spike_result = []
combined_result = []

# =========================
# PROCESS FILES
# =========================
for idx, file_path in enumerate(all_files, start=1):
    file_name = os.path.basename(file_path)
    state_name = file_name.replace(".csv", "")
    print(f"[{idx}/{total_files}] Processing: {file_name}")

    try:
        df = pd.read_csv(file_path, encoding="latin1")
        df.columns = df.columns.str.strip()

        # Identify dengue column
        dengue_cols = [c for c in df.columns if "Dengue" in c]
        if not dengue_cols:
            print("⚠️ No dengue column → skipped\n")
            continue
        dengue_col = dengue_cols[0]

        # Date & year/month
        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
        df["year"] = df["Data"].dt.year
        df["month"] = df["Data"].dt.month
        df = df[(df["year"] >= 2017) & (df["year"] <= 2021)]

        # Climate columns
        temp_col = [c for c in df.columns if "Temperatura" in c][0]
        rain_col = [c for c in df.columns if "Precip" in c][0]
        hum_col = [c for c in df.columns if "Umidade" in c][0]

        # Monthly aggregation
        monthly = df.groupby(["year", "month"]).agg({
            dengue_col: "mean",
            temp_col: "mean",
            rain_col: "mean",
            hum_col: "mean"
        }).reset_index()

        # Fill missing values forward/backward
        monthly = monthly.ffill().bfill()

        # Climate risk thresholds
        monthly["climate_favourable"] = (
            ((monthly[temp_col] >= 22) & (monthly[temp_col] <= 32)).astype(int) +
            (monthly[rain_col] > 50).astype(int) +
            (monthly[hum_col] > 70).astype(int)
        )
        # Take months where at least 2 conditions are favourable
        monthly["climate_favourable"] = (monthly["climate_favourable"] >= 2).astype(int)

        # Detect dengue spikes or max cases
        monthly = monthly.sort_values("month")
        monthly["prev"] = monthly[dengue_col].shift(1)
        monthly["spike"] = ((monthly[dengue_col] > monthly["prev"] * 1.5) |
                            (monthly[dengue_col] == monthly[dengue_col].max())).astype(int)

        # =========================
        # Store results per year
        # =========================
        for year in monthly["year"].unique():
            data_year = monthly[monthly["year"] == year]

            fav_months = data_year[data_year["climate_favourable"] == 1]["month"].tolist()
            spike_months = data_year[data_year["spike"] == 1]["month"].tolist()
            matched_months = [m for m in fav_months if m in spike_months]

            climate_result.append({
                "state": state_name,
                "year": year,
                "favourable_months": ",".join(map(str, fav_months)) if fav_months else "-",
                "spike_months_for_climate": ",".join(map(str, matched_months)) if matched_months else "-"
            })
            spike_result.append({
                "state": state_name,
                "year": year,
                "spike_months": ",".join(map(str, spike_months)) if spike_months else "-"
            })
            combined_result.append({
                "state": state_name,
                "year": year,
                "matched_months": ",".join(map(str, matched_months)) if matched_months else "-"
            })

        print("✅ Done\n")

    except Exception as e:
        print(f"❌ Error processing {file_name}: {e}\n")

# =========================
# CREATE DATAFRAMES AND PIVOT
# =========================
climate_df = pd.DataFrame(climate_result).pivot(index="state", columns="year", values=["favourable_months","spike_months_for_climate"])
spike_df = pd.DataFrame(spike_result).pivot(index="state", columns="year", values="spike_months")
combined_df = pd.DataFrame(combined_result).pivot(index="state", columns="year", values="matched_months")

# =========================
# CALCULATE PEAK MONTHS
# =========================
def parse_months(val):
    if val == "-" or pd.isna(val):
        return []
    return [int(float(x)) for x in str(val).split(",")]

# Combined CSV parsing
parsed_combined = combined_df.applymap(parse_months)

# State-wise peak month
state_peak = {}
for state in parsed_combined.index:
    all_months = []
    for year in parsed_combined.columns:
        all_months.extend(parsed_combined.loc[state, year])
    state_peak[state] = max(set(all_months), key=all_months.count) if all_months else "-"

combined_df["state_peak_month"] = combined_df.index.map(state_peak)

# Year-wise peak month
year_peak = {}
for year in parsed_combined.columns:
    all_months = []
    for state in parsed_combined.index:
        all_months.extend(parsed_combined.loc[state, year])
    year_peak[year] = max(set(all_months), key=all_months.count) if all_months else "-"

year_peak_row = pd.DataFrame([year_peak], index=["year_peak_month"])
combined_df = pd.concat([combined_df, year_peak_row])

# =========================
# Add peak columns to dengue spike CSV
# =========================
parsed_spike = spike_df.applymap(parse_months)

# State-wise peak
spike_state_peak = {}
for state in parsed_spike.index:
    all_months = []
    for year in parsed_spike.columns:
        all_months.extend(parsed_spike.loc[state, year])
    spike_state_peak[state] = max(set(all_months), key=all_months.count) if all_months else "-"

spike_df["state_peak_month"] = spike_df.index.map(spike_state_peak)

# Year-wise peak
spike_year_peak = {}
for year in parsed_spike.columns:
    all_months = []
    for state in parsed_spike.index:
        all_months.extend(parsed_spike.loc[state, year])
    spike_year_peak[year] = max(set(all_months), key=all_months.count) if all_months else "-"

spike_year_peak_row = pd.DataFrame([spike_year_peak], index=["year_peak_month"])
spike_df = pd.concat([spike_df, spike_year_peak_row])

# =========================
# Save all CSVs
# =========================
climate_df.to_csv(os.path.join(OUTPUT_PATH, "climate_favourable_months.csv"))
spike_df.to_csv(os.path.join(OUTPUT_PATH, "dengue_spike_months.csv"))
combined_df.to_csv(os.path.join(OUTPUT_PATH, "combined_climate_spike.csv"))

print("🎉 All CSVs saved in 'processed' folder with peak months included!")