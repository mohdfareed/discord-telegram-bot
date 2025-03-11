#!/bin/sh

source .venv/bin/activate

if [ "$DEBUG" = "true" ]; then
    exec poetry run bot -d start
else
    exec poetry run bot start
fi
