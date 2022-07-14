#!/bin/bash

# The patch disables pyppeteer launcher's signal handling (line 307 in
# pyppeteer_patch.py) since it causes an error when jobs are run in 
# a thread created by Apscheduler. In order to patch the launcher
# file in a virtual environment, the location of the file will be:
#
# /venv/lib/python3.10/site-packages/pyppeteer/launcher.py
#
# Background and discussion:
# https://docs.python.org/3/library/signal.html#signals-and-threads
# https://bugs.python.org/issue38904 (comment by Eric Snow)

cp patches/pyppeteer_patch.py /usr/local/lib/python3.10/site-packages/pyppeteer/launcher.py
