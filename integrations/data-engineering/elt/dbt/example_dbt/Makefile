VENV=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
DBT=$(VENV)/bin/dbt

export DBT_PROFILES_DIR=$(CURDIR)

.PHONY: help venv deps seed run test all clean ingest

help:
	@echo "Targets: venv, deps, seed, run, test, all, ingest, clean"

venv:
	python3 -m venv $(VENV)

deps: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

seed: deps
	$(DBT) seed

run: deps
	$(DBT) run

test: deps
	$(DBT) test

all: seed run test

ingest:
	bash scripts/ingest_qalita.sh

clean:
	rm -rf target dbt_packages

