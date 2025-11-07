#!/bin/bash
# Setup script for Project A (Pre-Improvement UI)

echo "Setting up Project A - Pre-Improvement UI"
echo "=========================================="

# Create virtual environment
python -m venv venv

# Activate virtual environment
if [ -f venv/Scripts/activate ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

echo ""
echo "Setup complete!"
echo "To run tests: ./run_tests.sh"
