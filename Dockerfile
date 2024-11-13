# syntax=docker/dockerfile:1

FROM python:3.7-slim-buster
LABEL maintainer="koussaila.moulouel@u-pe.fr"

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get clean

RUN apt-get update
RUN apt-get install -y build-essential cmake
RUN apt-get install -y libgtk-3-dev
RUN apt-get install -y libboost-all-dev
RUN apt-get install ffmpeg libsm6 libxext6 -y

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN apt-get update

COPY . .

#CMD [ "python3", "server.py"]