#!/bin/sh
#
# Setup virtual environment.

# Variables
VENV="env"
REQ="requirements.txt"

main () {
  version_check
  venv_create
  venv_activate
}

# Check python3 and pip3
version_check() {
  if ! check_cmd python3; then
    warn "Please install python3"
    exit 1
  fi
  if ! check_cmd pip3; then
    warn "Please install pip3"
    exit 1
  fi
}

# Create virtual environment
venv_create() {
  if ! check_exist "${VENV}"; then
    python3 -m venv ${VENV}
    ok "Virtual environment created"
  else
    info "Virtual environment existed"
  fi
}

# Activate virtual environment
venv_activate() {
  if check_exist "${VENV}"; then
    source ${VENV}/bin/activate
    ok "Virtual environment activated"
  else
    err "Unable to find virtual environment"
  fi

  pip install --upgrade pip

  # Install packages by requirements file
  if check_exist "${REQ}"; then
    pip install -r ${REQ}
    ok "Packages installed"
  fi
}

#
# Utils
#

# Colors
CLEAR='\033[2K'
NC='\033[0m'
BLACK='\033[0;30m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'

info() {
  printf "\r${CLEAR}  [ ${BLUE}..${NC} ] $1\n"
}

ok() {
  printf "\r${CLEAR}  [ ${GREEN}OK${NC} ] $1\n"
}

warn() {
  printf "\r${CLEAR}  [ ${YELLOW}!!${NC} ] $1\n"
}

err() {
  printf "\r${CLEAR}  [ ${RED}ERR${NC} ] $1\n"
  exit
}

check_cmd() {
  command -v "$1" >/dev/null 2>&1
}

check_exist() {
  test -e "$1" >/dev/null 2>&1
}

main "$@"