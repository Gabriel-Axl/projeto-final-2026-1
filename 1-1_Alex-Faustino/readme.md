# Churn Prediction Agent

## Executando localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

cd backend
uvicorn app:app --reload
```

## Executando com Docker

```bash
docker compose up --build
```

Swagger:

http://localhost:8000/docs

exemplo de alto risco

{
  "gender": "Female",
  "SeniorCitizen": 1,
  "Partner": "No",
  "Dependents": "No",
  "tenure": 2,
  "PhoneService": "Yes",
  "MultipleLines": "Yes",
  "InternetService": "Fiber optic",
  "OnlineSecurity": "No",
  "OnlineBackup": "No",
  "DeviceProtection": "No",
  "TechSupport": "No",
  "StreamingTV": "Yes",
  "StreamingMovies": "Yes",
  "Contract": "Month-to-month",
  "PaperlessBilling": "Yes",
  "PaymentMethod": "Electronic check",
  "MonthlyCharges": 105.80,
  "TotalCharges": 211.60
}

exemplo de baixo risco

{
  "gender": "Male",
  "SeniorCitizen": 0,
  "Partner": "Yes",
  "Dependents": "Yes",
  "tenure": 72,
  "PhoneService": "Yes",
  "MultipleLines": "Yes",
  "InternetService": "DSL",
  "OnlineSecurity": "Yes",
  "OnlineBackup": "Yes",
  "DeviceProtection": "Yes",
  "TechSupport": "Yes",
  "StreamingTV": "No",
  "StreamingMovies": "No",
  "Contract": "Two year",
  "PaperlessBilling": "No",
  "PaymentMethod": "Bank transfer (automatic)",
  "MonthlyCharges": 49.90,
  "TotalCharges": 3592.80
}