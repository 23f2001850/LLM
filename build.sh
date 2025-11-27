#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing Playwright browsers with dependencies..."
playwright install --with-deps chromium

echo "Build completed successfully!"
