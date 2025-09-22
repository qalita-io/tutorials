.PHONY: venv install run ingest-file

VENV=.venv
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
ACT=source $(VENV)/bin/activate

venv:
	python -m venv $(VENV)

install: venv
	$(PIP) install -r requirements.txt

run:
	$(PY) run_ge_and_ingest.py --suite retail_suite --data data/retail.csv

ingest-file:
	$(PY) ingest_ge_results.py --file artifacts/last_validation_result.json
