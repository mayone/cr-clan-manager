SHELL := $(shell which bash)

VENV := .venv
PYTHON := ${VENV}/bin/python
PIP := ${VENV}/bin/pip

init: prepare_venv

prepare_venv: ${VENV}/bin/activate

${VENV}/bin/activate:
	command source venv_setup.sh

install-dev: init
	${PIP} install -r requirements-dev.txt

lint: install-dev
	${VENV}/bin/ruff check .
	${VENV}/bin/ruff format --check .

format: install-dev
	${VENV}/bin/ruff check --fix .
	${VENV}/bin/ruff format .

test: install-dev
	${PYTHON} -m pytest tests/ -v

run: init
	${PYTHON} manager.py

clean:
	rm -rf ${VENV}

.PHONY: init prepare_venv install-dev lint format test run clean
