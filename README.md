# Nous Aggregator

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue)](https://www.python.org/downloads/release/python-3100/)
[![Django 4.05](https://img.shields.io/badge/django-4.0-blue)](https://docs.djangoproject.com/en/4.0/)
[![Django CI](https://github.com/pi-sigma/test/actions/workflows/django.yml/badge.svg)](https://github.com/pi-sigma/test/actions/workflows/django.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/pi-sigma/test/blob/main/LICENSE.md)

[https://www.nous-aggregator.com](https://www.nous-aggregator.com)

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

Open the file with the editor of your choice and set the following values:
```
DATABASE_HOST=db
DATABASE_PORT=5432
```

Build the Docker image (can take a while the first time around):
```sh
docker-compose build
```

Start the web container in detached mode (attempting to start the container for the scheduler at this point will result in an error because the database is empty):
```sh
docker-compose up -d web
```

Initialize the database:
```sh
docker-compose run web python manage.py loaddata fixtures/languages.json
docker-compose run web python manage.py loaddata fixtures/pub_types.json
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
paths: ["sections/world", "sections/national"]
regex: "/[0-9]{4}/[0-9]{2}/[0-9]{2}/"
headline: {"tag": "h1", "attrs": {}},
body: {"tag": "section", "attrs": {"id": "body-text"}},
```
This will tell the scraper to follow links on `https://www.example.com/sections/world` and `https://www.example.com/sections/national`, and to only extract data from pages whose link contains the specified pattern, ignoring everything else (thus it will scrape `https://www.example.com/2022/06/07/some-news-story.com` but not `https://www.example.com/policies.com`. Headlines should have an HTML tag `h1`, and the body should have an HTML tag `section` with an `id` attribute `body-text`. 

In order to extract data about the sources from the database, use the following command while the web container is running (the commands for the other tables are analogous):
```sh
docker-compose run web python manage.py dumpdata articles.source --indent 2 > fixtures/sources.json
```

## Development
Make sure [Python 3.10](https://www.python.org/downloads/) is installed on your system.

Create a virtual environment in the root directory of the app and activate it:
```sh
python3.10 -m venv venv
. venv/bin/activate
```
Install the requirements:
```sh
python -m pip install -r requirements/common.txt
python -m pip install -r requirements/dev.txt
```
The following script runs Pytype and Mypy, builds the Docker image, and runs Pytest inside the container:
```sh
./build.sh
```

The project contains a `yml` for a workflow ("Django CI") which is triggered every time the code is pushed to GitHub.
To make this work, you need to create two action secrets on GitHub (`DATABASE_HOST`: `db`, `DATABASE_PORT`: `5432`).
Or simply delete the .github folder to remove the workflow.

You can also run the app without Docker using the familiar `python manage.py runserver` (for the web server) and `python manage.py scrape` (for the scraper). This can be useful for testing/debugging settings for the scraper in connection with a VPN, which is not trivial to set up with Docker. However, make sure you have a Postgres database listening on port `5433` or change the database configuration in `settings.py`. Also see the next point.


## Issues
Sometimes it is necessary to render JavaScript on a webpage before any information can be extracted.
To achieve this, the scraper of this app makes use of the [requests-html](https://requests.readthedocs.io/projects/requests-html/en/latest/) library, which in turn uses [pyppeteer](https://github.com/miyakogi/pyppeteer) under the hood, a headless Chromium browser.

Pyppeteer uses a `SIGTERM` signal to terminate the browser process, which is fine when run on its own, but creates a problem in the present context.
The scraping jobs are scheduled to run in a separate thread created by [Apscheduler](https://apscheduler.readthedocs.io/en/3.x/) (potentially many threads, but the present setup uses only one).
However, according to the [Python Documentation](https://docs.python.org/3/library/signal.html#signals-and-threads) on signals and threads:

> Python signal handlers are always executed in the main Python thread of the main interpreter, even if the signal was received in another thread. This means that signals can’t be used as a means of inter-thread communication. You can use the synchronization primitives from the threading module instead.
>
> Besides, only the main thread of the main interpreter is allowed to set a new signal handler.


As a result, every job that requires the rendering of JavaScript fails and produces the following error:
```
ValueError: signal only works in main thread
```
Additional information and discussion of this sort of issue can be found [here](https://bugs.python.org/issue38904).

I've created a temporary workaround by disabling pyppeteer launcher's signal handling.
The patch is applied automatically during the build of the Docker image.
When the containers are started, the program runs normally.
If you want to run the app outside a Docker container, you will need to create a virtual environment and install the requirements as usual, then overwrite the launcher settings by hand (see the script `patches/pyppeteer_patch.sh` for hints on how to do this).
