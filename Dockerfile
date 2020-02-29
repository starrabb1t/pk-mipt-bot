FROM python:3.7.2-slim-stretch

WORKDIR /opt/app

COPY __init__.py /opt/app/ai_storage/
COPY json_utils.py /opt/app/ai_storage/
COPY storage.py /opt/app/ai_storage/
COPY utils.py /opt/app/ai_storage/

COPY main.py /opt/app/

RUN apt update -y &&\
    apt install -y python3-numpy python3-scipy &&\
    pip install python-telegram-bot==12.0.0b1 &&\
    pip install gensim==3.8.1 &&\
    pip install pymystem3==0.2.0 &&\
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
    htop \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT [ "/opt/app/main.py" ]