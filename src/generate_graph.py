import os
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# PATHS
# =========================
DATA_PATH = r"C:\Users\srila\OneDrive\Documents\CDH\Dengue-Brasil-Arboviroses-Dataset-Brazil-Dengue-Arboviral-Diseases-Dataset\DengueDataset\data"

OUTPUT_PATH = r"C:\Users\srila\OneDrive\Documents\CDH\data\graphs"
os.makedirs(OUTPUT_PATH, exist_ok=True)

# =========================
# SELECTED STATES
# =========================
SELECTED_STATES = [
    "dengue_29_bahia.csv",
    "dengue_31_minas_gerais.csv",
    "dengue_33_rio_de_janeiro.csv",
    "dengue_35_são_paulo.csv",
    "dengue_51_mato_grosso.csv"
]

# =========================
# PROCESS
# =========================
for root, dirs, files in os.walk(DATA_PATH):
    for file in files:

        if file in SELECTED_STATES:

            file_path = os.path.join(root, file)
            print(f"Processing {file}...")

            try:
                df = pd.read_csv(file_path, encoding="latin1")

                df.columns = df.columns.str.strip()
                dengue_col = [col for col in df.columns if "Dengue" in col][0]

                df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
                df["year"] = df["Data"].dt.year
                df["month"] = df["Data"].dt.month

                df = df[(df["year"] >= 2017) & (df["year"] <= 2021)]

                monthly = df.groupby(["year", "month"])[dengue_col].mean().reset_index()

                state_name = file.replace(".csv", "")

                # =========================
                # 🔥 CREATE SUBPLOTS
                # =========================
                years = sorted(monthly["year"].unique())

                fig, axes = plt.subplots(2, 3, figsize=(12, 8))  # grid
                axes = axes.flatten()

                for i, year in enumerate(years):
                    data_year = monthly[monthly["year"] == year]

                    axes[i].plot(data_year["month"], data_year[dengue_col])
                    axes[i].set_title(str(year))
                    axes[i].set_xlabel("Month")
                    axes[i].set_ylabel("Cases")

                # Remove empty subplot (if 5 years)
                if len(years) < 6:
                    for j in range(len(years), 6):
                        fig.delaxes(axes[j])

                fig.suptitle(state_name, fontsize=14)

                # Save
                graph_path = os.path.join(OUTPUT_PATH, f"{state_name}_combined.png")
                plt.tight_layout()
                plt.savefig(graph_path)
                plt.close()

            except Exception as e:
                print(f"❌ Error in {file}: {e}")

print("\n✅ Combined graphs generated!")