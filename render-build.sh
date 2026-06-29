#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Download the background browser engine binaries required by Playwright
playwright install chromium