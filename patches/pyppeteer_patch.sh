#!/bin/bash

# The patch disables pyppeteer launcher's signal handling (line 307 in
# pyppeteer_patch.py) since it causes an error when the scraper module is
# imported into the scheduler, where the main thread is running
# (articles/management/apscheduler).
#
# Background:
# https://bugs.python.org/issue38904 (comment by Eric Snow)
# https://www.pythonfixing.com/2022/02/fixed-running-pypupeteer-in-flask-gives.html

cp patches/pyppeteer_patch.py /usr/local/lib/python3.10/site-packages/pyppeteer/launcher.py
