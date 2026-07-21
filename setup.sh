#!/bin/bash -e

# Init git submodules (pyliczba)
git submodule update --init --recursive

# Setup and activate virtual python env
python3 -m venv wxenv
source wxenv/bin/activate

# Update and install requirements
pip install --upgrade pip
pip install -r requirements.txt

# Initiate .env file
cp .env.example .env
