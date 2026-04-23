import streamlit as st
import pandas as pd
import joblib
import json
import matplotlib.pyplot as plt

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="AI Prediction Dashboard",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
<style>

/* -------------------------------
🌌 Premium Background
------------------------------- */
.stApp {
    background: radial-gradient(circle at 20% 50%, rgba(6, 182, 212, 0.15), rgba(0, 0, 0, 0.95)),
                url("https://images.unsplash.com/photo-1531297484001-80022131f5a1");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* -------------------------------
🧊 Glassmorphism Container
------------------------------- */
.block-container {
    background: rgba(10, 20, 40, 0.65);
    backdrop-filter: blur(16px);
    border-radius: 28px;
    padding: 2rem 2.5rem;
    border: 1px solid rgba(56, 189, 248, 0.3);
    box-shadow: 0 25px 45px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    margin: 1rem auto;
}

/* -------------------------------
🎯 Headings - Neon Effect
------------------------------- */
h1 {
    background: linear-gradient(135deg, #38bdf8, #a855f7, #06b6d4);
    background-size: 200% auto;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    font-weight: 800;
    font-size: 2.5rem;
    text-align: center;
    margin-bottom: 1.5rem;
    animation: shimmer 3s linear infinite;
}

@keyframes shimmer {
    0% { background-position: 0% center; }
    100% { background-position: 200% center; }
}

h2, h3 {
    color: #7dd3fc;
    font-weight: 600;
    border-left: 4px solid #06b6d4;
    padding-left: 1rem;
    margin-top: 1.5rem;
}

/* -------------------------------
🔘 Premium Buttons
------------------------------- */
.stButton > button {
    background: linear-gradient(95deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%);
    background-size: 200% auto;
    color: white;
    font-weight: 700;
    border-radius: 40px;
    padding: 0.75rem 2rem;
    border: none;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    letter-spacing: 0.5px;
    box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
    width: 100%;
}

.stButton > button:hover {
    background-position: 100% center;
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(6, 182, 212, 0.5);
}

.stButton > button:active {
    transform: translateY(1px);
}

/* -------------------------------
📦 Input Fields - Futuristic
------------------------------- */
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background: rgba(15, 25, 45, 0.9) !important;
    color: #f1f5f9 !important;
    border-radius: 14px !important;
    border: 1px solid #334155 !important;
    padding: 0.6rem 1rem !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
}

.stNumberInput > div > div > input:focus,
.stSelectbox > div > div:focus-within {
    border-color: #06b6d4 !important;
    box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.2) !important;
    outline: none !important;
}

/* Labels */
.stNumberInput label, .stSelectbox label {
    color: #94a3b8 !important;
    font-weight: 500 !important;
    margin-bottom: 0.25rem !important;
}

/* -------------------------------
📊 Tabs - Premium Design
------------------------------- */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 16px;
    padding: 0.5rem;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 12px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    color: #94a3b8;
    transition: all 0.3s;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(6, 182, 212, 0.2);
    color: #7dd3fc;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #06b6d4, #3b82f6);
    color: white;
    box-shadow: 0 4px 12px rgba(6, 182, 212, 0.4);
}

/* -------------------------------
📈 Result Cards
------------------------------- */
.success-message, .error-message {
    border-radius: 20px;
    padding: 1.25rem;
    margin: 1rem 0;
    backdrop-filter: blur(8px);
    font-weight: 700;
    letter-spacing: 0.3px;
    animation: slideIn 0.5s ease-out;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.success-message {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.9), rgba(5, 150, 105, 0.95));
    border-left: 5px solid #6ee7b7;
    box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);
}

.error-message {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.9), rgba(220, 38, 38, 0.95));
    border-left: 5px solid #fca5a5;
    box-shadow: 0 8px 20px rgba(239, 68, 68, 0.3);
}

/* -------------------------------
📊 Metrics & Values
------------------------------- */
[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #38bdf8, #a78bfa);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

[data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
    font-weight: 500 !important;
}

/* -------------------------------
🎨 Charts Container
------------------------------- */
[data-testid="stPlotlyChart"] {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 20px;
    padding: 1rem;
    border: 1px solid rgba(56, 189, 248, 0.2);
}

/* -------------------------------
📱 Sidebar (if exists)
------------------------------- */
[data-testid="stSidebar"] {
    background: rgba(10, 20, 40, 0.8);
    backdrop-filter: blur(16px);
    border-right: 1px solid rgba(56, 189, 248, 0.2);
}

/* -------------------------------
✨ Custom Scrollbar
------------------------------- */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: rgba(15, 25, 45, 0.8);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #06b6d4, #8b5cf6);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #0891b2, #7c3aed);
}

/* -------------------------------
🎪 Expanders
------------------------------- */
[data-testid="stExpander"] details {
    background: rgba(15, 25, 45, 0.6);
    border-radius: 16px;
    border: 1px solid rgba(56, 189, 248, 0.2);
}

[data-testid="stExpander"] summary {
    color: #7dd3fc;
    font-weight: 600;
    padding: 0.75rem;
}

/* -------------------------------
📱 Responsive Design
------------------------------- */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem;
        border-radius: 20px;
    }
    
    h1 {
        font-size: 1.8rem;
    }
    
    .stButton > button {
        padding: 0.6rem 1rem;
    }
}

/* -------------------------------
🎭 Animations
------------------------------- */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.element-container {
    animation: fadeIn 0.6s ease-in;
}

/* -------------------------------
🏷️ Badge/Label Styling
------------------------------- */
.stAlert {
    background: rgba(6, 182, 212, 0.2);
    border: 1px solid #06b6d4;
    border-radius: 12px;
    color: #7dd3fc;
}

/* -------------------------------
📊 Dataframe Styling
------------------------------- */
.dataframe {
    background: rgba(15, 25, 45, 0.8);
    border-radius: 16px;
    overflow: hidden;
}

.dataframe th {
    background: linear-gradient(135deg, #06b6d4, #3b82f6);
    color: white;
    padding: 12px;
}

.dataframe td {
    color: #e2e8f0;
    padding: 10px;
    border-bottom: 1px solid rgba(56, 189, 248, 0.2);
}
/* =======================================================
📊 MATPLOTLIB GRAPH (st.pyplot) — PREMIUM UPGRADE
======================================================= */

/* Graph container card */
div[data-testid="stPyplot"] {
    margin-top: 1rem;
    padding: 1.5rem;
    border-radius: 22px;

    background: linear-gradient(
        145deg,
        rgba(10, 20, 40, 0.85),
        rgba(30, 41, 59, 0.55)
    );

    backdrop-filter: blur(12px);

    border: 1px solid rgba(56, 189, 248, 0.25);

    box-shadow:
        0 10px 30px rgba(0, 0, 0, 0.4),
        0 0 25px rgba(6, 182, 212, 0.25),
        inset 0 0 12px rgba(255, 255, 255, 0.05);

    transition: all 0.35s ease;
}

/* Hover glow */
div[data-testid="stPyplot"]:hover {
    transform: translateY(-3px) scale(1.01);

    box-shadow:
        0 20px 50px rgba(0, 0, 0, 0.6),
        0 0 40px rgba(6, 182, 212, 0.45),
        inset 0 0 16px rgba(255, 255, 255, 0.08);
}

/* Canvas smoothing */
canvas {
    border-radius: 16px !important;
}

/* Chart title glow */
div[data-testid="stPyplot"] + div h3 {
    text-shadow: 0 0 12px rgba(6,182,212,0.6);
}

/* Fade animation */
@keyframes graphFade {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}

div[data-testid="stPyplot"] {
    animation: graphFade 0.6s ease;
}


</style>
""", unsafe_allow_html=True)

# -------------------------------
# Paths
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

df_full = pd.read_csv(DATA_PATH)
df_full = df_full.sort_values(by=["YEAR", "Q_NUM"])

# -------------------------------
# Title
# -------------------------------
st.title("📊 AI Prediction Dashboard")

# -------------------------------
# Tabs (FIXED ORDER)
# -------------------------------
tab1, tab2, tab3 = st.tabs([
    "🦟 Disease Prediction",
    "📈 Stock Prediction",
    "📊 Visualizations"
])

# =========================================================
# 🦟 TAB 1 — DISEASE PREDICTION
# =========================================================
with tab1:

    st.subheader("🦟 Disease Risk Prediction")

    col1, col2 = st.columns(2)

    with col1:
        R_d = st.number_input("Rainfall (mm)", value=300.0, key="d_r")
        T_d = st.number_input("Temperature (°C)", value=28.0, key="d_t")
        H_d = st.number_input("Humidity (RH)", value=70.0, key="d_h")

    if st.button("Predict Disease Risk", key="d_btn"):

        dengue_model = joblib.load(f"{MODEL_DIR}/dengue_model.pkl")
        malaria_model = joblib.load(f"{MODEL_DIR}/malaria_model.pkl")

        input_df = pd.DataFrame([{
            "R": R_d,
            "T": T_d,
            "H": H_d
        }])

        d_pred = dengue_model.predict(input_df)[0]
        m_pred = malaria_model.predict(input_df)[0]

        st.subheader("📊 Results")

        if d_pred == 1:
            st.markdown('<div class="error-message">🦟 Dengue Risk: HIGH</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-message">🦟 Dengue Risk: LOW</div>', unsafe_allow_html=True)

        if m_pred == 1:
            st.markdown('<div class="error-message">🦟 Malaria Risk: HIGH</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-message">🦟 Malaria Risk: LOW</div>', unsafe_allow_html=True)

# =========================================================
# 📈 TAB 2 — STOCK PREDICTION
# =========================================================
with tab2:

    st.subheader("🔮 Stock Prediction")

    col1, col2 = st.columns(2)

    with col1:
        stock = st.selectbox("Select Stock", stocks, key="stock_pred")
        R = st.number_input("Rainfall (mm)", value=200.0, key="s_r")
        T = st.number_input("Temperature (°C)", value=30.0, key="s_t")
        H = st.number_input("Humidity (RH)", value=20.0, key="s_h")

    if st.button("Predict Stock", key="s_btn"):

        model = joblib.load(f"{MODEL_DIR}/model_{stock}.pkl")

        input_data = {
            "R": R,
            "T": T,
            "H": H,
            "TEMP_HUM": T * H,
            "RAIN_HUM": R * H
        }

        df = pd.DataFrame([input_data])
        df = df[features]

        prediction = model.predict(df)[0]
        probs = model.predict_proba(df)[0]

        if prediction == 1:
            st.markdown('<div class="success-message">📈 Stock likely to INCREASE</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error-message">📉 Stock likely to DECREASE</div>', unsafe_allow_html=True)

        st.write(f"Confidence: {round(probs[1], 3)}")

# =========================================================
# 📊 TAB 3 — VISUALIZATION (IMPROVED)
# =========================================================
with tab3:

    st.subheader("📊 Data Insights")

    stock_viz = st.selectbox("Select Stock", stocks, key="stock_viz")

    graph_type = st.selectbox(
        "Select Graph",
        ["Stock Price Trend", "Rainfall vs Price", "Temperature vs Price", "Humidity vs Price"],
        key="graph_type"
    )

    price_col = f"{stock_viz}_PRICE"

    fig, ax = plt.subplots(figsize=(8, 5))

    # 🎨 Dark styling
    fig.patch.set_facecolor('#020617')
    ax.set_facecolor('#020617')

    # =========================================================
    # 📈 STOCK TREND
    # =========================================================
    if graph_type == "Stock Price Trend":

        x = df_full["YEAR"].astype(str) + "-Q" + df_full["Q_NUM"].astype(str)
        y = df_full[price_col]

        ax.plot(x, y, linewidth=2)

        ax.set_title(f"{stock_viz} Price Trend", color='white')
        ax.set_xlabel("Time", color='white')
        ax.set_ylabel("Price", color='white')

        plt.xticks(rotation=45)

        st.info("📈 Shows how stock price changes over time.")

    # =========================================================
    # 🌧️ RAINFALL VS PRICE
    # =========================================================
    elif graph_type == "Rainfall vs Price":

        x = df_full["R"]
        y = df_full[price_col]

        ax.scatter(x, y, alpha=0.7)

        # 🔥 Trendline
        import numpy as np
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        ax.plot(x, p(x), linewidth=2)

        ax.set_title(f"Rainfall vs {stock_viz} Price", color='white')
        ax.set_xlabel("Rainfall (mm)", color='white')
        ax.set_ylabel("Price", color='white')

        corr = x.corr(y)
        st.info(f"🌧️ Correlation: {round(corr,2)} (Rainfall vs Price)")

    # =========================================================
    # 🌡️ TEMPERATURE VS PRICE
    # =========================================================
    elif graph_type == "Temperature vs Price":

        x = df_full["T"]
        y = df_full[price_col]

        ax.scatter(x, y, alpha=0.7)

        import numpy as np
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        ax.plot(x, p(x), linewidth=2)

        ax.set_title(f"Temperature vs {stock_viz} Price", color='white')
        ax.set_xlabel("Temperature (°C)", color='white')
        ax.set_ylabel("Price", color='white')

        corr = x.corr(y)
        st.info(f"🌡️ Correlation: {round(corr,2)} (Temperature vs Price)")



    # =========================================================
    # 💧 HUMIDITY VS PRICE
    # =========================================================
    elif graph_type == "Humidity vs Price":

        x = df_full["H"]
        y = df_full[price_col]

        ax.scatter(x, y, alpha=0.7)

        import numpy as np
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        ax.plot(x, p(x), linewidth=2)

        ax.set_title(f"Humidity vs {stock_viz} Price", color='white')
        ax.set_xlabel("Humidity (RH)", color='white')
        ax.set_ylabel("Price", color='white')

        corr = x.corr(y)
        st.info(f"💧 Correlation: {round(corr,2)} (Humidity vs Price)")

    # 🎯 Axis + ticks color
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')

    st.pyplot(fig)