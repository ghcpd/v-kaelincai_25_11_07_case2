#!/bin/bash
# Setup script for Project A (Pre-Improvement)

set -e

echo "Setting up Project A (Pre-Improvement)..."

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Create necessary directories
mkdir -p screenshots logs results data

echo "Setup complete!"
echo "To activate the virtual environment, run: source venv/bin/activate"

