#!/bin/bash

docker stop pk-mipt-bot
docker rm pk-mipt-bot

docker run -d \
-e TELEGRAM_API_TOKEN \
-v $(pwd)/data:/opt/app/data \
--name pk-mipt-bot pk-mipt-bot:latest
