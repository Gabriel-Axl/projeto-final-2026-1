VENV?=.venv
# prefer venv python if present, otherwise fallback to system python3
PYTHON := $(if $(wildcard $(VENV)/bin/python),$(VENV)/bin/python,python3)
# prefer venv pip if present, otherwise fallback to pip3
PIP := $(if $(wildcard $(VENV)/bin/pip),$(VENV)/bin/pip,pip3)

.PHONY: setup run docker-test test evaluate clean \
	fly-deploy fly-update fly-pause fly-resume fly-destroy fly-vol-delete

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

# Fly.io convenience targets. Set APP to your Fly app name or export it in your shell.
APP ?= my-churn-app

fly-deploy:
	@echo "Deploying to Fly: $(APP)"
	flyctl deploy --config fly.toml --app $(APP)

fly-update: fly-deploy
	@echo "Update complete."

fly-pause:
	@echo "Scaling VMs to 0 (pause) for app: $(APP)"
	flyctl scale vm count 0 --app $(APP)

fly-resume:
	@echo "Scaling VMs to 1 (resume) for app: $(APP)"
	flyctl scale vm count 1 --app $(APP)

fly-destroy:
	@echo "Destroying Fly app: $(APP) (this is irreversible)"
	@read -p "Are you sure? Type 'yes' to continue: " ans; \
	if [ "$$ans" = "yes" ]; then \
		flyctl apps destroy $(APP) --yes; \
		echo "App destroyed."; \
	else \
		echo "Aborted."; \
	fi

fly-vol-delete:
	@echo "Listing volumes (region may be required):"; \
	flyctl volumes list --app $(APP) || true; \
	@read -p "Enter volume name to delete (or leave empty to skip): " vol; \
	if [ -n "$$vol" ]; then \
		flyctl volumes delete $$vol --yes || true; \
		echo "Requested deletion of $$vol"; \
	else \
		echo "No volume deleted."; \
	fi
