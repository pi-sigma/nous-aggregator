#
# Base
#
FROM python:3.11-slim-bookworm AS base

# build deps
RUN apt-get update && apt-get upgrade && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev

# get latest version of pip
RUN pip install pip -U

# install requirements
COPY /requirements/* /app/requirements/
RUN pip install -r /app/requirements/dev.txt

# pyppeteer deps (https://stackoverflow.com/a/71935536)
RUN xargs apt-get install -y --no-install-recommends < /app/requirements/pyppeteer_deps.txt


#
# Final
#
FROM python:3.11-slim-bookworm AS final

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
        postgresql-client

# copy backend deps
COPY --from=base /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=base /usr/local/bin/ /usr/local/bin/

COPY . /app
WORKDIR /app

# create user and drop privileges
RUN useradd -m pi-sigma
RUN chown -R pi-sigma /app
USER pi-sigma

RUN python manage.py collectstatic --link --no-input
