#!/bin/bash

docker stop pk-mipt-bot
docker rm pk-mipt-bot

export TELEGRAM_API_TOKEN=1136290332:AAH6bzEYS-i0vN6zRJXHyL6z7Ifiq78UWvk

docker run -d \
-e TELEGRAM_API_TOKEN \
-v $(pwd)/data:/opt/app/data \
--name pk-mipt-bot pk-mipt-bot:latest
