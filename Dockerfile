FROM python:3.10-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements/* requirements/

RUN apt-get update \
  # psycopg2 + deps
  && apt-get install -y --no-install-recommends build-essential \
  && apt-get install -y --no-install-recommends libpq-dev \
  && pip install psycopg2 \
  # pyppeteer deps (cf. https://stackoverflow.com/a/71935536)
  && xargs apt-get install -y --no-install-recommends < requirements/pyppeteer_deps.txt \
  && pip install -r requirements/production.txt

COPY . /usr/src/app
WORKDIR /usr/src/app

RUN python manage.py collectstatic --link --no-input

RUN useradd -m myuser
USER myuser
