#!/bin/bash

docker stop pk-mipt-bot
docker rm pk-mipt-bot
docker rmi pk-mipt-bot:latest
docker build -t pk-mipt-bot .
mkdir data