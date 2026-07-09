VENV?=.venv
# prefer venv python if present, otherwise fallback to system python3
PYTHON := $(if $(wildcard $(VENV)/bin/python),$(VENV)/bin/python,python3)
# prefer venv pip if present, otherwise fallback to pip3
PIP := $(if $(wildcard $(VENV)/bin/pip),$(VENV)/bin/pip,pip3)

.PHONY: setup run docker-test test evaluate clean

setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r backend/requirements.txt

run:
	$(PYTHON) -m uvicorn backend.app:app --reload --port 8000

docker-build:
	docker compose build

docker-up:
	docker compose up --build

test:
	$(PYTHON) -m pytest -q backend

evaluate:
	$(PYTHON) backend/evaluate.py --model backend/models/churn_model.pkl --data backend/data/Telco-Customer-Churn.csv --out backend/models

clean:
	rm -rf $(VENV)
