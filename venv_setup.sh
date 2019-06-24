#!/bin/sh

# Variables
venv="env"

# Create virtual environment
venv_create()
{
	if ! [ -d "$venv" ]; then
		python3 -m venv $venv
		echo "virtual environment created"
	else
		echo "virtual environment existed"
	fi
}

# Activate virtual environment
venv_activate()
{
	if [ -d "$venv" ]; then
		source $venv/bin/activate
		echo "virtual environment activated"
	else
		echo "Unable to find virtual environment"
		exit 1
	fi

	# Install packages by requirements file
	pip install -r requirements.txt
}

venv_create
venv_activate