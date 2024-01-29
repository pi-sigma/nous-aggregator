# Nous Aggregator

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/downloads/release/python-3110/)
[![Django 5.01](https://img.shields.io/badge/django-5.0-blue)](https://docs.djangoproject.com/en/5.0/)
[![Django CI](https://github.com/pi-sigma/nous-aggregator/actions/workflows/django.yml/badge.svg)](https://github.com/pi-sigma/test/actions/workflows/django.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/pi-sigma/test/blob/main/LICENSE.md)


## Overview
A content aggregator that collects metadata about articles from newspapers, journals, blogs, etc.
The scraper uses information about the structure of the targeted pages as well as regular expressions in order to scrape selectively and filter the results.
To facilitate the start of a new project, the data required by the scraper is extracted to files in the [fixtures](https://github.com/pi-sigma/nous-aggregator/tree/main/fixtures) directory.

Inspired by [AllTop](https://alltop.com/).

## Installation
Make sure [Docker](https://docs.docker.com/get-docker/) is installed on your system.

Clone the repository into a directory of your choice: 
```sh
mkdir MYAPPDIR
git clone https://github.com/pi-sigma/nous-aggregator.git MYAPPDIR
```

Inside the new directory, create a file for the environment variables:
```sh
touch .env
```
Open the file with the editor of your choice and set the environment variables.
See [env-sample](https://github.com/pi-sigma/nous-aggregator/blob/main/env-sample) for instructions.

Build the Docker image:
```sh
docker-compose build
```

Start the web container in detached mode, apply the migrations, and initialize
the database:
```sh
docker-compose up -d web
docker-compose run web python manage.py migrate
docker-compose run web python manage.py loaddata fixtures/sources.json
```

Create a superuser for the Django app:
```sh
docker-compose run web python manage.py createsuperuser
```

Stop the containers:
```sh
docker-compose stop web
docker-compose stop db
```


## Usage
Start the Docker containers:
```sh
docker-compose up
```

You can access the page at one of the following addresses:
```
http://0.0.0.0:8000
http://127.0.0.1:8000
http://localhost:8000
```

If all went well, you should see the homepage of the app with a list of news sources arranged in a grid.
The grids are empty to begin with, but the celery workers will start right away and you should see the
first articles displayed shortly thereafter.

In order to extract data about the sources from the database, use the following command while the web container is running (the commands for the other tables are analogous):
```sh
docker-compose run web python manage.py dumpdata articles.source --indent 2 > fixtures/sources.json
```
