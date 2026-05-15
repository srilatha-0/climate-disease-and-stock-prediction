import streamlit as st
import pandas as pd
import joblib
import json

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="AI Prediction Dashboard",
    page_icon="📈",
    layout="wide"
)

# =========================================================
# PREMIUM CSS
# (YOUR EXISTING CSS KEPT + EXTRA METRICS TAB CSS ADDED)
# =========================================================
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
🧊 Glass Container
------------------------------- */
.block-container {
    background: rgba(10, 20, 40, 0.65);
    backdrop-filter: blur(16px);
    border-radius: 28px;
    padding: 2rem 2.5rem;
    border: 1px solid rgba(56, 189, 248, 0.3);
    box-shadow: 0 25px 45px rgba(0,0,0,0.35);
    margin-top: 1rem;
}

/* -------------------------------
🎯 Heading
------------------------------- */
h1 {
    background: linear-gradient(135deg,#38bdf8,#a855f7,#06b6d4);
    -webkit-background-clip:text;
    color:transparent;
    font-size:2.6rem;
    font-weight:900;
    text-align:center;
}

h2,h3 {
    color:#7dd3fc;
    border-left:4px solid #06b6d4;
    padding-left:1rem;
}

/* -------------------------------
🔘 Buttons
------------------------------- */
.stButton > button {
    width:100%;
    border:none;
    border-radius:40px;
    padding:0.75rem 1rem;
    font-weight:700;
    color:white;
    background:linear-gradient(95deg,#06b6d4,#3b82f6,#8b5cf6);
    transition:0.3s ease;
}

.stButton > button:hover {
    transform:translateY(-2px);
    box-shadow:0 10px 30px rgba(6,182,212,0.45);
}

/* -------------------------------
📦 Inputs
------------------------------- */
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(15,25,45,0.9) !important;
    color:white !important;
    border-radius:14px !important;
    border:1px solid #334155 !important;
}

/* -------------------------------
📊 Tabs
------------------------------- */
.stTabs [data-baseweb="tab-list"] {
    gap:0.5rem;
    background:rgba(0,0,0,0.35);
    padding:0.5rem;
    border-radius:16px;
}

.stTabs [data-baseweb="tab"] {
    border-radius:12px;
    padding:0.75rem 1.5rem;
    color:#94a3b8;
    font-weight:700;
}

.stTabs [aria-selected="true"] {
    background:linear-gradient(135deg,#06b6d4,#3b82f6);
    color:white !important;
}

/* -------------------------------
📈 Result Cards
------------------------------- */
.success-message {
    background:linear-gradient(135deg,#10b981,#059669);
    color:white;
    padding:1.2rem;
    border-radius:20px;
    font-weight:700;
    margin:1rem 0;
}

.error-message {
    background:linear-gradient(135deg,#ef4444,#dc2626);
    color:white;
    padding:1.2rem;
    border-radius:20px;
    font-weight:700;
    margin:1rem 0;
}

/* =====================================================
📊 METRICS TAB ADVANCED CSS
===================================================== */

.metric-box {
    background: rgba(15,25,45,0.82);
    border:1px solid rgba(56,189,248,0.22);
    border-radius:20px;
    padding:1.2rem;
    margin-bottom:1rem;
    box-shadow:0 10px 20px rgba(0,0,0,0.25);
}

.metric-title {
    color:#94a3b8;
    font-size:0.95rem;
    margin-bottom:0.4rem;
}

.metric-value {
    font-size:2rem;
    font-weight:900;
    background:linear-gradient(135deg,#38bdf8,#a855f7);
    -webkit-background-clip:text;
    color:transparent;
}

.rank-gold {
    color:#facc15;
    font-weight:800;
}

.rank-silver {
    color:#cbd5e1;
    font-weight:800;
}

.rank-bronze {
    color:#fb923c;
    font-weight:800;
}

/* dataframe */
.dataframe {
    background:rgba(15,25,45,0.85);
    border-radius:16px;
}

.dataframe th {
    background:linear-gradient(135deg,#06b6d4,#3b82f6);
    color:white;
}

.dataframe td {
    color:#e2e8f0;
}

/* Scrollbar */
::-webkit-scrollbar {
    width:10px;
}

::-webkit-scrollbar-thumb {
    background:linear-gradient(135deg,#06b6d4,#8b5cf6);
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# PATHS
# =========================================================
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "backend", "data", "models")
META_PATH = os.path.join(BASE_DIR, "backend", "data", "model_meta.json")

# =========================================================
# LOAD META
# =========================================================
with open(META_PATH, "r") as f:
    meta = json.load(f)

features = meta["features"]
stocks = meta["stocks"]

# =========================================================
# METRICS DATA
# =========================================================
stock_metrics = {
    "APOLLOHOSP": {"accuracy": 0.8, "confusion_matrix": [[0,1],[1,8]]},
    "AUROPHARMA": {"accuracy": 0.8, "confusion_matrix": [[0,0],[2,8]]},
    "CIPLA": {"accuracy": 0.6364, "confusion_matrix": [[2,2],[2,5]]},
    "DRREDDY": {"accuracy": 0.6364, "confusion_matrix": [[0,2],[2,7]]},
    "LUPIN": {"accuracy": 0.8182, "confusion_matrix": [[0,0],[2,9]]},
    "SUNPHARMA": {"accuracy": 0.8182, "confusion_matrix": [[0,0],[2,9]]}
}

disease_metrics = {
    "DENGUE": {
        "accuracy": 0.9130434782608695,
        "confusion_matrix": [[64,0],[8,20]]
    },
    "MALARIA": {
        "accuracy": 0.9347826086956522,
        "confusion_matrix": [[68,4],[2,18]]
    }
}

# =========================================================
# TITLE
# =========================================================
st.title("📊 AI Prediction Dashboard")

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3 = st.tabs([
    "🦟 Disease Prediction",
    "📈 Stock Prediction",
    "📊 Metrics Dashboard"
])

# =========================================================
# TAB 1 DISEASE
# =========================================================
with tab1:

    st.subheader("🦟 Disease Risk Prediction")

    col1, col2 = st.columns(2)

    with col1:
        R_d = st.number_input("Rainfall (mm)", value=300.0, key="d_r")
        T_d = st.number_input("Temperature (°C)", value=28.0, key="d_t")
        H_d = st.number_input("Humidity (RH)", value=70.0, key="d_h")

    if st.button("Predict Disease Risk"):

        dengue_model = joblib.load(f"{MODEL_DIR}/dengue_model.pkl")
        malaria_model = joblib.load(f"{MODEL_DIR}/malaria_model.pkl")

        input_df = pd.DataFrame([{
            "R": R_d,
            "T": T_d,
            "H": H_d
        }])

        d_pred = dengue_model.predict(input_df)[0]
        m_pred = malaria_model.predict(input_df)[0]

        if d_pred == 1:
            st.markdown('<div class="error-message">🦟 Dengue Risk: HIGH</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-message">🦟 Dengue Risk: LOW</div>', unsafe_allow_html=True)

        if m_pred == 1:
            st.markdown('<div class="error-message">🦟 Malaria Risk: HIGH</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-message">🦟 Malaria Risk: LOW</div>', unsafe_allow_html=True)

# =========================================================
# TAB 2 STOCK
# =========================================================
with tab2:

    st.subheader("📈 Stock Prediction")

    col1, col2 = st.columns(2)

    with col1:
        stock = st.selectbox("Select Stock", stocks)
        R = st.number_input("Rainfall (mm)", value=200.0)
        T = st.number_input("Temperature (°C)", value=30.0)
        H = st.number_input("Humidity (RH)", value=20.0)

    if st.button("Predict Stock Movement"):

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

        pred = model.predict(df)[0]
        probs = model.predict_proba(df)[0]

        if pred == 1:
            st.markdown(
                f'<div class="success-message">📈 {stock} is likely to INCREASE in upcoming quarter based on current climate conditions.</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="error-message">📉 {stock} is likely to DECREASE in upcoming quarter based on current climate conditions.</div>',
                unsafe_allow_html=True
            )

        st.info(f"Confidence Score: {round(max(probs),3)}")

# =========================================================
# TAB 3 METRICS ONLY
# =========================================================
with tab3:

    st.subheader("📊 Model Performance Dashboard")

    # -----------------------------------------------------
    # TOP MODELS
    # -----------------------------------------------------
    ranking = sorted(stock_metrics.items(), key=lambda x: x[1]["accuracy"], reverse=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title rank-gold">🥇 Best Model</div>
            <div class="metric-value">{ranking[0][0]}</div>
            Accuracy: {ranking[0][1]["accuracy"]*100:.2f}%
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title rank-silver">🥈 Runner Up</div>
            <div class="metric-value">{ranking[1][0]}</div>
            Accuracy: {ranking[1][1]["accuracy"]*100:.2f}%
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title rank-bronze">🥉 Third Place</div>
            <div class="metric-value">{ranking[2][0]}</div>
            Accuracy: {ranking[2][1]["accuracy"]*100:.2f}%
        </div>
        """, unsafe_allow_html=True)

    # -----------------------------------------------------
    # INNER TABS
    # -----------------------------------------------------
    sub1, sub2 = st.tabs(["📈 Stock Metrics", "🦟 Disease Metrics"])

    # =====================================================
    # STOCK TABLE
    # =====================================================
    with sub1:

        rows = []

        for name, vals in stock_metrics.items():
            cm = vals["confusion_matrix"]

            rows.append({
                "Stock": name,
                "Accuracy %": round(vals["accuracy"] * 100, 2),
                "TN": cm[0][0],
                "FP": cm[0][1],
                "FN": cm[1][0],
                "TP": cm[1][1]
            })

        df_stock = pd.DataFrame(rows)
        st.dataframe(df_stock, use_container_width=True)

        avg_acc = df_stock["Accuracy %"].mean()

        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">Average Stock Model Accuracy</div>
            <div class="metric-value">{avg_acc:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    # =====================================================
    # DISEASE TABLE
    # =====================================================
    with sub2:

        rows = []

        for name, vals in disease_metrics.items():
            cm = vals["confusion_matrix"]

            rows.append({
                "Disease Model": name,
                "Accuracy %": round(vals["accuracy"] * 100, 2),
                "TN": cm[0][0],
                "FP": cm[0][1],
                "FN": cm[1][0],
                "TP": cm[1][1]
            })

        df_dis = pd.DataFrame(rows)
        st.dataframe(df_dis, use_container_width=True)

        avg_dis = df_dis["Accuracy %"].mean()

        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">Average Disease Model Accuracy</div>
            <div class="metric-value">{avg_dis:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.success("✅ Metrics dashboard loaded successfully.")