FROM python:3.6-buster

RUN mkdir /beakerbot
WORKDIR /beakerbot
COPY . /beakerbot

RUN apt update && \
    apt install -y \
    libxml2-dev \
    libxslt-dev \
    libenchant1c2a \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install -r requirements.txt

CMD python -m cloudbot