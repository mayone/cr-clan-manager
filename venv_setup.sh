#!/bin/sh

. ./utils.sh

# Variables
VENV="env"
REQ="requirements.txt"

main () {
	venv_create
	venv_activate
}

# Create virtual environment
venv_create() {
	if ! check_exist "${VENV}"; then
		python3 -m venv ${VENV}
		info "Virtual environment created"
	else
		info "Virtual environment existed"
	fi
}

# Activate virtual environment
venv_activate() {
	if check_exist "${VENV}"; then
		source ${VENV}/bin/activate
		info "Virtual environment activated"
	else
		info "Unable to find virtual environment"
		exit 1
	fi

	# Install packages by requirements file
	if check_exist "${REQ}"; then
		pip3 install -r ${REQ}
		info "Packages installed"
	fi
}

main