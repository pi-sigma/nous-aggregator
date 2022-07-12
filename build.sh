#!/bin/bash

# Checks the source code for type errors, builds the docker image,
# runs tests inside the container.

mypy
if [ $? != 0 ]; then
	echo "Mypy raised some error(s): aborting build"
	exit 1
fi
pytype
if [ $? != 0 ]; then
	echo "Pytype raised some error(s): aborting build"
	exit 1
fi
docker-compose build
if [ $? != 0 ]; then
	echo "Build failed"
	exit 1
fi
docker-compose run --rm web pytest --disable-warnings articles/tests.py
if [ $? != 0 ]; then
	echo "Some test(s) failed"
fi
