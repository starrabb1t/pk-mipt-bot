#!/bin/bash

docker stop mr-clappy-bot
docker rm mr-clappy-bot

export TELEGRAM_API_TOKEN=871197060:AAHw2FiSrom_d3KD0Ob23kClbXLyaZKskVQ

docker run -d \
-e TELEGRAM_API_TOKEN \
-v $(pwd)/data:/opt/app/data \
--name mr-clappy-bot mr-clappy-bot:latest
