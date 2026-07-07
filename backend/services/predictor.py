import joblib
import pandas as pd


class ChurnPredictor:

    def __init__(self):
        self.model = joblib.load("models/churn_model.pkl")

    def predict(self, customer):

        df = pd.DataFrame([customer])

        probability = self.model.predict_proba(df)[0][1]

        classification = (
            "Alto risco"
            if probability >= 0.5
            else "Baixo risco"
        )

        return {
            "probabilidade": round(float(probability), 4),
            "classificacao": classification
        }