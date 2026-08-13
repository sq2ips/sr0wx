#!/bin/bash -e

# Safe to re-run, e.g. after changing requirements.txt.
# Pass -r to install the Raspberry Pi requirements instead.

cd "$(dirname "$(realpath "$0")")"

REQUIREMENTS="requirements.txt"
if [ "$1" = "-r" ]; then
    REQUIREMENTS="requirements-rpi.txt"
fi

# Init git submodules (pyliczba)
git submodule update --init --recursive

# Setup and activate virtual python env
python3 -m venv wxenv
source wxenv/bin/activate

# Update and install requirements
pip install --upgrade pip
pip install -r "${REQUIREMENTS}"

# Initiate .env file, never overwrite the one already there -- it holds the
# API keys and the APRS passcode
if [ -f .env ]; then
    echo ".env already exists, leaving it alone."
else
    cp .env.example .env
    echo "Created .env from .env.example, fill it in before running sr0wx.py."
fi
