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

---

**Avaliação do Modelo (métricas e plots)**

Use o script de avaliação para gerar métricas e gráficos (ROC, PR, matriz de confusão) e um limiar recomendado.

Com `Makefile` você pode rodar:

```
make setup       # cria venv e instala dependências
make evaluate    # executa backend/evaluate.py e salva resultados em backend/models
```

O script salva em `backend/models`:
- `metrics.txt` — resumo legível
- `metrics.json` — métricas em JSON
- `roc.png`, `pr.png`, `confusion.png` — gráficos

Exemplo de saída (trecho de `metrics.txt`):

```
Evaluation results
==================
n_test: 1409
ROC AUC: 0.7800
PR AUC: 0.5600

Per-class metrics (class 0 = No churn, class 1 = Churn):
Precision: class0=0.82, class1=0.60
Recall:    class0=0.89, class1=0.47
F1:        class0=0.85, class1=0.53
Support:   class0=1035, class1=374

Confusion matrix (rows=true, cols=pred):
[[923, 112], [198, 176]]

Best threshold (max F1): 0.500 with F1=0.5300
```
