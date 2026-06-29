#!/usr/bin/env bash
# exit on error
set -o errexit

# Install python dependencies
pip install -r requirements.txt

# Install Chromium browser binaries AND their required Linux system libraries
playwright install chromium
playwright install-deps chromium