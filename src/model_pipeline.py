import pandas as pd
import os
import joblib
import optuna
import shap
import matplotlib.pyplot as plt

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from xgboost import XGBClassifier


# ======================
# LOAD DATA
# ======================
def load_data():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base_dir, "data", "processed", "final_merged_data.csv")

    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])

    return df


# ======================
# PREPARE DATA
# ======================
def prepare_data(df):

    df["target"] = (df["return"] > 0).astype(int)

    features = [
        "temp", "rainfall", "humidity",
        "outbreak", "outbreak_score"
    ]

    X = df[features]
    y = df["target"]

    return X, y, df


# ======================
# BACKTEST SPLIT (🔥 KEY CHANGE)
# ======================
def time_based_split(df, X, y):

    df = df.sort_values("date")

    train_idx = df["date"] < "2022-01-01"
    test_idx = df["date"] >= "2022-01-01"

    X_train = X[train_idx]
    X_test = X[test_idx]
    y_train = y[train_idx]
    y_test = y[test_idx]

    return X_train, X_test, y_train, y_test


# ======================
# OPTUNA OBJECTIVE
# ======================
def objective(trial, X_train, X_test, y_train, y_test):

    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 300),
        "max_depth": trial.suggest_int("max_depth", 3, 8),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.15),
        "subsample": trial.suggest_float("subsample", 0.7, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.7, 1.0),
        "random_state": 42,
        "use_label_encoder": False,
        "eval_metric": "logloss",
        "verbosity": 0
    }

    model = XGBClassifier(**params)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    return accuracy_score(y_test, preds)


# ======================
# TRAIN OR LOAD MODEL
# ======================
def train_or_load_model(X, y, df):

    base_dir = os.path.dirname(os.path.dirname(__file__))
    model_path = os.path.join(base_dir, "models", "xgb_model.pkl")

    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    # 🔥 TIME SPLIT
    X_train, X_test, y_train, y_test = time_based_split(df, X, y)

    if os.path.exists(model_path):
        print("✅ Loading saved model...")
        model = joblib.load(model_path)

    else:
        print("🚀 Training with BACKTESTING (real-world split)...\n")

        optuna.logging.set_verbosity(optuna.logging.WARNING)

        study = optuna.create_study(direction="maximize")
        study.optimize(
            lambda trial: objective(trial, X_train, X_test, y_train, y_test),
            n_trials=20
        )

        print("🔥 Best Parameters:")
        print(study.best_params)

        model = XGBClassifier(
            **study.best_params,
            random_state=42,
            use_label_encoder=False,
            eval_metric="logloss",
            verbosity=0
        )

        model.fit(X_train, y_train)

        joblib.dump(model, model_path)
        print(f"\n💾 Model saved at {model_path}")

    # ======================
    # EVALUATION
    # ======================
    preds = model.predict(X_test)

    print("\n📊 BACKTEST PERFORMANCE (2022–2023)")
    print("=" * 40)

    print(f"Accuracy: {accuracy_score(y_test, preds):.4f}\n")

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, preds), "\n")

    print("Classification Report:")
    print(classification_report(y_test, preds))

    return model


# ======================
# SHAP
# ======================
def explain_model(model, X):

    base_dir = os.path.dirname(os.path.dirname(__file__))
    plot_path = os.path.join(base_dir, "models", "shap_summary.png")

    if os.path.exists(plot_path):
        print("✅ SHAP already computed.")
        return

    print("\n🔍 Running SHAP...")

    X_sample = X.sample(n=500, random_state=42)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)

    shap.summary_plot(shap_values, X_sample, show=False)

    plt.savefig(plot_path, bbox_inches="tight")
    print(f"📊 Saved at {plot_path}")


# ======================
# MAIN
# ======================
if __name__ == "__main__":

    df = load_data()
    X, y, df = prepare_data(df)

    model = train_or_load_model(X, y, df)

    explain_model(model, X)