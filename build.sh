#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing Playwright chromium browser (without system deps)..."
PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/ms-playwright playwright install chromium --no-shell

echo "Build completed successfully!"
