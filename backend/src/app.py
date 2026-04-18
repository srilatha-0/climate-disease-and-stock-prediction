import streamlit as st
import pandas as pd
import joblib
import json
import matplotlib.pyplot as plt

# -------------------------------
# Page Config (Professional Look)
# -------------------------------
st.set_page_config(
    page_title="Stock Prediction Dashboard",
    page_icon="📈",
    layout="wide"
)

# -------------------------------
# Custom Styling (IMPROVED)
# -------------------------------
st.markdown("""
<style>
.main {
    background-color: #000000;
    color: #f8fafc;
    font-family: 'Segoe UI', system-ui, sans-serif;
}

h1, h2, h3 {
    color: #06b6d4;
    font-weight: 600;
    margin-bottom: 1rem;
}

.stButton>button {
    background: linear-gradient(135deg, #06b6d4 0%, #0ea5e9 100%);
    color: white;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    background: linear-gradient(135deg, #0891b2 0%, #0284c7 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);
}

.stSelectbox > div > div {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    color: #f8fafc;
}

.stNumberInput > div > div > input {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    color: #f8fafc;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background-color: #1e293b;
    border-radius: 8px 8px 0 0;
    padding: 12px 24px;
    font-weight: 500;
}

.stTabs [aria-selected="true"] {
    background-color: #06b6d4;
    color: white;
}

div[data-testid="stVerticalBlock"] {
    gap: 1rem;
}

.success-message {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    padding: 1rem;
    border-radius: 8px;
    font-weight: 600;
}

.error-message {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    color: white;
    padding: 1rem;
    border-radius: 8px;
    font-weight: 600;
}

.confidence-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 600;
}

.strong {
    background-color: #10b981;
    color: white;
}

.moderate {
    background-color: #f59e0b;
    color: white;
}

.weak {
    background-color: #ef4444;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Paths (UNCHANGED)
# -------------------------------
MODEL_DIR = "../data/models"
META_PATH = "../data/model_meta.json"
DATA_PATH = "../data/climate_stock_extended.csv"

# -------------------------------
# Load metadata
# -------------------------------
with open(META_PATH, "r") as f:
    meta = json.load(f)

features = meta["features"]
stocks = meta["stocks"]

# Load dataset for graphs
df_full = pd.read_csv(DATA_PATH)
df_full = df_full.sort_values(by=["YEAR", "Q_NUM"])

# -------------------------------
# Title
# -------------------------------
st.title("📈 Stock Prediction Dashboard")
st.write("Predict stock movement using climate + recent price")

# -------------------------------
# Tabs
# -------------------------------
tab1, tab2 = st.tabs(["📊 Prediction", "📈 Visualizations"])

# =========================================================
# 📊 TAB 1 — PREDICTION
# =========================================================
with tab1:

    st.subheader("🔮 Make Prediction")

    col1, col2 = st.columns(2)

    with col1:
        stock = st.selectbox("Select Stock", stocks)
        R = st.number_input("Rainfall (R)", value=200.0)
        T = st.number_input("Temperature (T)", value=30.0)
        H = st.number_input("Humidity (H)", value=20.0)

    with col2:
        last_price = st.number_input("Last Stock Price", value=1000.0)

    # Predict
    if st.button("Predict"):

        model = joblib.load(f"{MODEL_DIR}/model_{stock}.pkl")

        input_data = {
            "R": R,
            "T": T,
            "H": H,
            "TEMP_HUM": T * H,
            "RAIN_HUM": R * H,
            "PRICE_LAG1": last_price
        }

        df = pd.DataFrame([input_data])
        df = df[features]

        prediction = model.predict(df)[0]
        probs = model.predict_proba(df)[0]

        st.subheader("📊 Result")

        if prediction == 1:
            st.markdown('<div class="success-message">📈 Stock likely to INCREASE</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error-message">📉 Stock likely to DECREASE</div>', unsafe_allow_html=True)

        st.write(f"Confidence (Increase): {round(probs[1], 3)}")

        # Confidence interpretation
        if probs[1] > 0.75:
            st.markdown('<span class="confidence-badge strong">💪 Strong Signal</span>', unsafe_allow_html=True)
        elif probs[1] > 0.6:
            st.markdown('<span class="confidence-badge moderate">👍 Moderate Signal</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="confidence-badge weak">⚠️ Weak Signal</span>', unsafe_allow_html=True)

        # Probability bar chart
        st.subheader("📊 Probability Breakdown")

        fig, ax = plt.subplots()
        ax.bar(["Decrease", "Increase"], probs, color=['#ef4444', '#10b981'])
        ax.set_ylabel("Probability")
        ax.set_facecolor("#d9dee7")
        fig.patch.set_facecolor("#a8aebd")
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.yaxis.label.set_color('white')
        st.pyplot(fig)

# =========================================================
# 📈 TAB 2 — VISUALIZATION
# =========================================================
with tab2:

    st.subheader("📊 Data Insights")

    stock_viz = st.selectbox("Select Stock for Visualization", stocks)

    graph_type = st.selectbox(
        "Select Graph",
        [
            "Stock Price Trend",
            "Rainfall vs Price",
            "Temperature vs Price",
            "Humidity vs Price"
        ]
    )

    price_col = f"{stock_viz}_PRICE"

    fig, ax = plt.subplots()

    if graph_type == "Stock Price Trend":
        ax.plot(
            df_full["YEAR"].astype(str) + "-Q" + df_full["Q_NUM"].astype(str),
            df_full[price_col],
            color='#06b6d4',
            linewidth=2
        )
        ax.set_title(f"{stock_viz} Price Trend", color='white')
        ax.set_xlabel("Time", color='white')
        ax.set_ylabel("Price", color='white')
        plt.xticks(rotation=45)
        ax.set_facecolor('#1e293b')
        fig.patch.set_facecolor('#0f172a')
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')

    elif graph_type == "Rainfall vs Price":
        ax.scatter(df_full["R"], df_full[price_col], color='#06b6d4', alpha=0.7)
        ax.set_title(f"Rainfall vs {stock_viz} Price", color='white')
        ax.set_xlabel("Rainfall", color='white')
        ax.set_ylabel("Price", color='white')
        ax.set_facecolor('#1e293b')
        fig.patch.set_facecolor('#0f172a')
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')

    elif graph_type == "Temperature vs Price":
        ax.scatter(df_full["T"], df_full[price_col], color='#06b6d4', alpha=0.7)
        ax.set_title(f"Temperature vs {stock_viz} Price", color='white')
        ax.set_xlabel("Temperature", color='white')
        ax.set_ylabel("Price", color='white')
        ax.set_facecolor('#1e293b')
        fig.patch.set_facecolor('#0f172a')
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')

    elif graph_type == "Humidity vs Price":
        ax.scatter(df_full["H"], df_full[price_col], color='#06b6d4', alpha=0.7)
        ax.set_title(f"Humidity vs {stock_viz} Price", color='white')
        ax.set_xlabel("Humidity", color='white')
        ax.set_ylabel("Price", color='white')
        ax.set_facecolor('#1e293b')
        fig.patch.set_facecolor('#0f172a')
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')

    st.pyplot(fig)
