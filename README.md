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

Start the web container in detached mode (attempting to start the container for the scheduler/scraper at this point will result in an error because the database is empty):
```sh
docker-compose up -d web
```

Apply migrations:
```sh
docker-compose run web python manage.py migrate
```

Initialize the database:
```sh
docker-compose run web python manage.py loaddata fixtures/sources.json
```

Create a superuser for the Django app (you will be prompted to choose a username and password):
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
There are no articles in the database yet, and the scraper won't do any work right away because it is set to run every 8 hours (this setting can be changed by modifying the code of the scheduler in `articles/managment/commands/scrape.py`).
However, you can run the scraper manually from the admin area:
```
http://localhost:8000/admin
```
Enter your username and password to log in, then go to "Django Jobs" in the panel on the left-hand side and select the job(s) you want to run.

Jobs can be tweaked and created from within the admin area. Here are some example settings:
```sh
base_url: "https://www.example.com/"
paths: ["path1/", "path2/"]
regex: "/[0-9]{4}/[0-9]{2}/[0-9]{2}/"
headline: {"tag": "h1", "attrs": {}},
summary: {"tag": "section", "attrs": {"class": "body-text"}},
```
This will tell the scraper to follow links on `https://www.example.com/path1/` and `https://www.example.com/path2/`, and to only extract data from pages whose link contains the specified pattern, ignoring everything else (thus it will scrape `https://www.example.com/2022/06/07/story.com` but not `https://www.example.com/policies.com`. Headlines should have an HTML tag `h1`, and the body should have an HTML tag `section` with a `class` attribute `body-text`.

In order to extract data about the sources from the database, use the following command while the web container is running (the commands for the other tables are analogous):
```sh
docker-compose run web python manage.py dumpdata articles.source --indent 2 > fixtures/sources.json
```

## Development
Make sure [Python 3.11](https://www.python.org/downloads/) is installed on your system.

create a virtual environment in the root directory of the app and activate it:
```sh
python3.10 -m venv venv
. venv/bin/activate
```
Install the requirements:
```sh
python -m pip install -r requirements/dev.txt
```
Run the tests:
```sh
pytest articles/tests.py
```
