#!/bin/sh

python -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install poetry
poetry install
