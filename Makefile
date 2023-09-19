VENV_BIN ?= python3 -m venv
VENV_DIR ?= venv
PIP_CMD ?= pip3

ifeq ($(OS), Windows_NT)
	VENV_ACTIVATE = $(VENV_DIR)/Scripts/activate
else
	VENV_ACTIVATE = $(VENV_DIR)/bin/activate
endif

VENV_RUN = . $(VENV_ACTIVATE)

usage: ## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/:.*##\s*/##/g' | awk -F'##' '{ printf "%-25s %s\n", $$1, $$2 }'

$(VENV_ACTIVATE): setup.py setup.cfg
	@test -d $(VENV_DIR) || $(VENV_BIN) $(VENV_DIR)
	@$(VENV_RUN); $(PIP_CMD) install --upgrade pip setuptools wheel plux
	@touch $(VENV_ACTIVATE)

venv: $(VENV_ACTIVATE) ## Create a new (empty) virtual environment

freeze: ## Run pip freeze -l in the virtual environment
	@$(VENV_RUN); pip freeze -l

install: install-lib install-dev ## Install full dependencies into venv

install-dev: venv ## Install requirements for development into venv
	@$(VENV_RUN); $(PIP_CMD) install -r requirements-dev.txt

install-lib: venv ## Install requirements for godaddypy into venv
	@$(VENV_RUN); $(PIP_CMD) install -r requirements.txt

test: ## Run tests via nose
	@$(VENV_RUN); nosetests

lint: ## Run linter
	@$(VENV_RUN); python -m pflake8 --show-source

format:
	@$(VENV_RUN); python -m black examples godaddypy tests

clean: ## Clean up everything
	rm -f .coverage
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf $(VENV_DIR)

clean-dist: ## Clean up python distribution directories
	rm -rf dist/
	rm -rf *.egg-info

.PHONY: usage freeze install install-dev install-lib test lint format clean clean-dist