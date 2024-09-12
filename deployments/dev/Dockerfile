FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --fix-missing \
    build-essential \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements /app/requirements

RUN pip install --no-cache-dir -r requirements/development.txt

COPY . /app

EXPOSE 8000
