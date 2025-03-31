#!/bin/sh

# import environment variables from .env file
set -a && source .env && set +a

if [ "$DEBUG" = "true" ]; then
    exec poetry run bot -d start
else
    exec poetry run bot start
fi
