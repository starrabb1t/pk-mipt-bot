#!/bin/bash

docker stop pk-mipt-bot
docker rm pk-mipt-bot

export TELEGRAM_API_TOKEN=871197060:AAHw2FiSrom_d3KD0Ob23kClbXLyaZKskVQ

docker run -d \
-e TELEGRAM_API_TOKEN \
-v $(pwd)/data:/opt/app/data \
--name pk-mipt-bot pk-mipt-bot:latest
