#!/bin/sh

# recreate the bot docker image
docker-compose build --no-cache
docker-compose up --detach
