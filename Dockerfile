FROM python:3.8-slim-buster
# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


COPY ./requirements.txt /app/requirements.txt

RUN pip3 install -r requirements.txt

# copy project
COPY . /app/
