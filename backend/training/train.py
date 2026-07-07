import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from sklearn.metrics import (
    classification_report,
    ConfusionMatrixDisplay,
    roc_auc_score
)

import matplotlib.pyplot as plt

# Carregar dataset
df = pd.read_csv("../data/Telco-Customer-Churn.csv")

# Remover coluna de ID
df.drop(columns=["customerID"], inplace=True)

# Corrigir TotalCharges
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

# Variável alvo
y = df["Churn"].map({"Yes": 1, "No": 0})
X = df.drop(columns=["Churn"])

# Colunas
categorical_cols = X.select_dtypes(include="object").columns.tolist()
numeric_cols = X.select_dtypes(exclude="object").columns.tolist()

# Pré-processamento
numeric_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="median"))
])

categorical_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer([
    ("num", numeric_transformer, numeric_cols),
    ("cat", categorical_transformer, categorical_cols)
])

# Pipeline
model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    ))
])

# Divisão treino/teste
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Treinar
model.fit(X_train, y_train)

# Avaliar
pred = model.predict(X_test)

pred_proba = model.predict_proba(X_test)[:, 1]

roc_auc = roc_auc_score(y_test, pred_proba)

print(f"ROC-AUC: {roc_auc:.4f}")

with open("../models/metrics.txt", "a") as f:
    f.write(f"\nROC-AUC: {roc_auc:.4f}\n")

report = classification_report(y_test, pred)

ConfusionMatrixDisplay.from_predictions(y_test, pred)

plt.tight_layout()
plt.savefig("../models/confusion_matrix.png")
plt.close()

print(report)

with open("../models/metrics.txt", "w") as f:
    f.write(report)

# Salvar
joblib.dump(model, "../models/churn_model.pkl")

print("\nModelo salvo em backend/models/churn_model.pkl")