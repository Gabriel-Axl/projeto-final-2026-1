
import os
import sys
import types

import pytest

# ensure backend package imports work when tests are executed from repo root
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from services.predictor import ChurnPredictor
from services.validators import validate_customer
from services.ai_agent import AIAgent
from fastapi import HTTPException


class FakeModel:
	def predict_proba(self, df):
		# always predict 0.8 probability for churn
		return [[0.2, 0.8]]


def sample_customer():
	return {
		"gender": "Female",
		"SeniorCitizen": 0,
		"Partner": "No",
		"Dependents": "No",
		"tenure": 5,
		"PhoneService": "Yes",
		"MultipleLines": "No",
		"InternetService": "DSL",
		"OnlineSecurity": "Yes",
		"OnlineBackup": "No",
		"DeviceProtection": "No",
		"TechSupport": "No",
		"StreamingTV": "No",
		"StreamingMovies": "No",
		"Contract": "Month-to-month",
		"PaperlessBilling": "Yes",
		"PaymentMethod": "Electronic check",
		"MonthlyCharges": 50.0,
		"TotalCharges": 250.0,
	}


def test_predictor_predicts(monkeypatch):
	# patch joblib.load to return fake model
	monkeypatch.setattr("services.predictor.joblib.load", lambda path: FakeModel())

	predictor = ChurnPredictor()

	res = predictor.predict(sample_customer())

	assert "probabilidade" in res
	assert isinstance(res["probabilidade"], float)
	assert res["classificacao"] == "Alto risco"


def test_validate_customer_accepts_and_rejects():
	ok = sample_customer()
	# should not raise
	validate_customer(ok)

	bad = sample_customer()
	bad["tenure"] = -5
	with pytest.raises(HTTPException):
		validate_customer(bad)


def test_ai_agent_fallback_on_exception(monkeypatch):
	# force the external LLM call to raise
	import services.ai_agent as ai_agent_module

	def raise_exc(*a, **k):
		raise Exception("simulated failure")

	# replace the generate_content method to simulate failure
	monkeypatch.setattr(ai_agent_module.client.models, "generate_content", raise_exc)

	agent = AIAgent()
	res = agent.explain(sample_customer(), {"probabilidade": 0.1})

	assert isinstance(res, dict)
	assert "explicacao" in res
	assert "acao_sugerida" in res


def test_ai_agent_handles_invalid_json(monkeypatch):
	import services.ai_agent as ai_agent_module

	class Resp:
		def __init__(self, text):
			self.text = text

	# simulate model returning invalid JSON
	monkeypatch.setattr(ai_agent_module.client.models, "generate_content", lambda *a, **k: Resp("not a json"))

	agent = AIAgent()
	res = agent.explain(sample_customer(), {"probabilidade": 0.1})

	assert isinstance(res, dict)
	assert "explicacao" in res
	assert "acao_sugerida" in res
