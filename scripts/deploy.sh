#!/bin/sh

usage="usage: $0 [-p|--prod]"
if [ "$#" -gt 1 ]; then echo $usage && exit 1; fi
if [ "$1" != "-p" ] && [ "$1" != "--prod" ] && [ "$1" != "" ]; then
    echo $usage && exit 1
fi

# update the bot
if [ $1 ]; then
    echo "production deployment"
    git fetch --all
    git pull --rebase --auto-stash
fi

# recreate the image
docker-compose pull
docker-compose build --no-cache
docker-compose up --detach
