SHELL := /bin/bash
VENV := env
PYTHON := ${VENV}/bin/python

init: prepare_venv

prepare_venv: ${VENV}/bin/activate

${VENV}/bin/activate:
	command source venv_setup.sh

test:
	# py.test tests

run: init
	${PYTHON} manager.py

clean:
	rm -rf ${VENV}

.PHONY: init prepare_venv test run