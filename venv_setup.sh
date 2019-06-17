#!/bin/sh

# Variables
venv="virtualenv"

# Create virtual environment
if ! [ -d "$venv" ]; then
	python3 -m venv $venv
	echo "virtual environment created"
else
	echo "virtual environment existed"
fi

# Activate virtual environment
if [ -d "$venv" ]; then
	source $venv/bin/activate
	echo "virtual environment activated"
else
	echo "Unable to find virtual environment"
	exit 1
fi

# Install packages by requirements file
pip install -r requirements.txt
