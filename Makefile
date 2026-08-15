# Shortcuts, so you don't have to remember the exact commands.
#
#     make help     - list everything
#     make setup    - install the Python packages
#     make check    - verify your environment
#     make demo     - run the whole pipeline on fake model + sample data
#     make run      - the real experiment on YOUR data
#     make test     - run the test suite
#
# On Windows: `make` may not be installed. Either use Git Bash / WSL, or just
# copy the command out of the recipe below and paste it into PowerShell.

PY ?= python3

.DEFAULT_GOAL := help
.PHONY: help setup check demo run analyze test lint clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	 | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

setup:  ## Install Python dependencies
	$(PY) -m pip install -r requirements.txt

check:  ## Verify Python, packages, data files and Ollama
	$(PY) python/misconception/check_setup.py

demo:  ## Full pipeline with the fake model + sample data (no Ollama needed)
	$(PY) python/misconception/run_experiment.py --mock --sample
	$(PY) python/misconception/analyze.py

run:  ## The real experiment, on YOUR data, with the local model
	$(PY) python/misconception/run_experiment.py
	$(PY) python/misconception/analyze.py

analyze:  ## Re-run only the analysis on existing predictions
	$(PY) python/misconception/analyze.py

test:  ## Run the test suite
	$(PY) -m pytest -q

clean:  ## Delete generated results and caches (your data/ is untouched)
	rm -rf python/results/*.csv python/results/*.png .pytest_cache python/misconception/__pycache__ python/tests/__pycache__
	@echo "Cleaned. python/data/ and docs/ were not touched."
