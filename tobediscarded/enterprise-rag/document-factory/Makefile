PYTHON ?= python
VENV ?= .venv
PIP := $(VENV)/Scripts/pip
PY := $(VENV)/Scripts/python

ifeq ($(OS),Windows_NT)
	PIP := $(VENV)/Scripts/pip.exe
	PY := $(VENV)/Scripts/python.exe
else
	PIP := $(VENV)/bin/pip
	PY := $(VENV)/bin/python
endif

.PHONY: venv install test dry-run generate-5 generate-50 generate-1000 clean

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(PIP) install -r requirements.txt

test:
	$(PY) -m pytest -q

dry-run:
	$(PY) -m src.main --documents 10 --start-year 2020 --end-year 2026 --seed 47 --output output --dry-run

generate-5:
	$(PY) -m src.main --documents 5 --start-year 2020 --end-year 2026 --seed 47 --output output --concurrency 3

generate-50:
	$(PY) -m src.main --documents 50 --start-year 2020 --end-year 2026 --seed 47 --output output --concurrency 3

generate-1000:
	$(PY) -m src.main --documents 1000 --start-year 2020 --end-year 2026 --seed 47 --output output --concurrency 3

clean:
	rm -rf output/raw output/failures output/manifests output/evaluation output/plans.json output/generation-summary.json
