import joblib
import pandas as pd


class ChurnPredictor:

    def __init__(self, model_path="models/churn_model.pkl", lazy=True):
        self.model_path = model_path
        self.model = None
        self.lazy = lazy
        if not lazy:
            self._load_model()

    def _load_model(self):
        try:
            # Use memory-mapping to reduce peak memory usage when loading large numpy arrays
            self.model = joblib.load(self.model_path, mmap_mode='r')
        except Exception as e:
            raise RuntimeError(f"Modelo indisponível: {e}")

    def predict(self, customer):
        if self.model is None:
            self._load_model()

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
