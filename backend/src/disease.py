import pandas as pd
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

# -------------------------------
# Paths
# -------------------------------
DATA_PATH = "../data/final_quarterly_dataset.csv"
MODEL_DIR = "../data/models"

os.makedirs(MODEL_DIR, exist_ok=True)

# -------------------------------
# Load dataset
# -------------------------------
df = pd.read_csv(DATA_PATH)

# -------------------------------
# Features (ONLY climate)
# -------------------------------
features = ["R", "T", "H"]

X = df[features]

# -------------------------------
# ===============================
# 🦟 DENGUE MODEL
# ===============================
# -------------------------------

y_dengue = df["DENGUE_TARGET"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y_dengue, test_size=0.2, random_state=42
)

dengue_model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

dengue_model.fit(X_train, y_train)

# Evaluate
y_pred = dengue_model.predict(X_test)

d_acc = accuracy_score(y_test, y_pred)
d_cm = confusion_matrix(y_test, y_pred)

print("\n🦟 DENGUE MODEL")
print("Accuracy:", d_acc)
print("Confusion Matrix:\n", d_cm)

# Save
joblib.dump(dengue_model, f"{MODEL_DIR}/dengue_model.pkl")


# -------------------------------
# ===============================
# 🦟 MALARIA MODEL
# ===============================
# -------------------------------
y_malaria = df["MALARIA_TARGET"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y_malaria, test_size=0.2, random_state=42
)

malaria_model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

malaria_model.fit(X_train, y_train)

# Evaluate
y_pred = malaria_model.predict(X_test)

m_acc = accuracy_score(y_test, y_pred)
m_cm = confusion_matrix(y_test, y_pred)

print("\n🦟 MALARIA MODEL")
print("Accuracy:", m_acc)
print("Confusion Matrix:\n", m_cm)

# Save
joblib.dump(malaria_model, f"{MODEL_DIR}/malaria_model.pkl")

print("\n✅ Climate-based Disease Models Trained Successfully!")

# -------------------------------
# Feature Importance (ADDED PART)
# -------------------------------
import matplotlib.pyplot as plt

# Dengue
plt.figure()
importances = dengue_model.feature_importances_
plt.bar(["R", "T", "H"], importances)
plt.title("Feature Importance (Dengue)")
plt.xlabel("Features")
plt.ylabel("Importance")
plt.show()

# Malaria (NEW)
plt.figure()
importances = malaria_model.feature_importances_
plt.bar(["R", "T", "H"], importances)
plt.title("Feature Importance (Malaria)")
plt.xlabel("Features")
plt.ylabel("Importance")
plt.show()