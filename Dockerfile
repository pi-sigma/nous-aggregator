# Base
FROM python:3.11-slim-bookworm AS BASE

# build deps
RUN apt update && apt upgrade && apt install -y --no-install-recommends \
        build-essential \
        libpq-dev

# get latest version of pip
RUN pip install pip -U

# install requirements
COPY /requirements/* /app/requirements/
RUN pip install -r /app/requirements/dev.txt


# Final
FROM python:3.11-slim-bookworm AS FINAL

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update && apt upgrade -y && apt install -y --no-install-recommends \
        postgresql-client

# copy backend deps
COPY --from=BASE /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=BASE /usr/local/bin/ /usr/local/bin/

COPY . /app
WORKDIR /app

# create user and drop privileges
RUN useradd -m nous_aggregator
RUN chown -R nous_aggregator /app
USER nous_aggregator

RUN python manage.py collectstatic --link --no-input
