FROM python:3.7.2-slim-stretch

WORKDIR /opt/app

COPY main.py /opt/app/
COPY storage.py /opt/app/

RUN apt update -y &&\
    apt install -y python3-numpy python3-scipy &&\
    pip install python-telegram-bot==12.0.0b1 &&\
    apt clean && rm -rf /var/lib/apt/lists/* &&\
    mkdir -p /opt/app &&\
    chmod -R 777 /opt/app/* /opt/app/*.py

RUN apt-get update \
    && apt-get install -y \
    build-essential \
    git \
    wget \
    unzip \
    nano \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT [ "/opt/app/main.py" ]