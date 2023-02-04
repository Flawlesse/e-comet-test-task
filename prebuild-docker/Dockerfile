FROM python:3.10.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get -y install cron nano
WORKDIR /app

RUN python -m pip install --upgrade pip
RUN pip install scrapy
RUN pip install scrapy-playwright
RUN playwright install
RUN playwright install-deps
