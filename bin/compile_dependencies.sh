#!/bin/bash

# Compile dependencies for production, CI, and development.
#
# Make sure that pip-tools is installed in your virtual environment
#
# From the project root:
#
#	./bin/compile_dependencies.sh
#
# Additionl flags/arguments are passed down to pip-compile. E.g. to update a package:
#
#	./bin/compile_dependencies.sh --upgrade-package django


export CUSTOM_COMPILE_COMMAND="./bin/compile_dependencies.sh"

# Base/production
pip-compile \
	"$@" \
	requirements/base.in

# CI
pip-compile \
	--output-file requirements/ci.txt \
	"$@" \
	requirements/base.txt \
	requirements/ci.in

# Development
pip-compile \
	--output-file requirements/dev.txt \
	"$@" \
	requirements/ci.txt \
	requirements/dev.in
