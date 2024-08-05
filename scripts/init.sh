#!/bin/bash

readonly VENV_NAME=".venv"
readonly COLOR_ESC=$(printf '\033')

function output_error() {
    echo "${COLOR_ESC}[31mERROR: ${@}${COLOR_ESC}[m" >&2
    return 0
}

function output_info() {
    echo "${COLOR_ESC}[1m${COLOR_ESC}[36m${@}${COLOR_ESC}[m${COLOR_ESC}[m"
    return 0
}

cd $(dirname $0)
cd ../src/

if [ -f $VENV_NAME ]; then
    output_error "file '${VENV_NAME}' is exists"
    exit 1
fi
if [ -d $VENV_NAME ]; then
    output_error "folder '${VENV_NAME}' is already exists"
    exit 2
fi

output_info "start initializing project..."
# venv
output_info "generating python venv"
python3 -m venv $VENV_NAME
. "${VENV_NAME}/bin/activate"

# update pip
output_info "upgrading pip of venv"
python3 -m pip install --upgrade pip

# install packages
output_info "installing required packages"
pip install -r requirements.txt

#fin
output_info "initializing finished successful!"
deactivate
