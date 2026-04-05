import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

# ── 1. Load dataset ──────────────────────────────────────
df = pd.read_csv("data/dataset.csv")
df.columns = df.columns.str.strip()
print("Columns found:", df.shape)

# ── 2. Find all unique symptoms ──────────────────────────
symptom_columns = [col for col in df.columns if col != "Disease"]

all_symptoms = set()
for col in symptom_columns:
    df[col] = df[col].astype(str).str.strip()
    unique_vals = df[col].dropna().unique()
    for val in unique_vals:
        if val not in ["0", "nan", ""]:
            all_symptoms.add(val)

all_symptoms = sorted(list(all_symptoms))
print(f"Total unique symptoms found: {len(all_symptoms)}")

# ── 3. Convert to binary matrix ──────────────────────────
# Each row = one disease record
# Each column = one symptom (1 if present, 0 if not)
def encode_row(row):
    present = set()
    for col in symptom_columns:
        val = str(row[col]).strip()
        if val not in ["0", "nan", ""]:
            present.add(val)
    return [1 if s in present else 0 for s in all_symptoms]

print("Encoding symptoms... please wait")
X = pd.DataFrame(
    [encode_row(row) for _, row in df.iterrows()],
    columns=all_symptoms
)
y = df["Disease"].str.strip()

print(f"Dataset shape: {X.shape}")
print(f"Total diseases: {y.nunique()}")

# ── 4. Save symptom list ─────────────────────────────────
os.makedirs("model", exist_ok=True)
joblib.dump(all_symptoms, "model/symptom_list.pkl")

# ── 5. Train/Test split ──────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ── 6. Train Random Forest ───────────────────────────────
print("\nTraining model... please wait")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ── 7. Accuracy ──────────────────────────────────────────
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {acc * 100:.2f}%")

# ── 8. Save model ────────────────────────────────────────
joblib.dump(model, "model/rf_model.pkl")
print("\nModel saved to model/rf_model.pkl ✅")
print("Symptom list saved to model/symptom_list.pkl ✅")