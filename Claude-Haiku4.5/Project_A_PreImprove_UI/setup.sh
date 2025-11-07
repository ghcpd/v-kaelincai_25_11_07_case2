#!/bin/bash
# Setup script for Project A - Pre-improvement UI

echo "Setting up Project A - Pre-improvement UI environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/Mac
    source venv/bin/activate
fi

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Install playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium firefox

# Copy test data
echo "Copying shared test data..."
if [ -f "../test_data.json" ]; then
    cp ../test_data.json data/
    echo "Test data copied successfully"
else
    echo "Warning: Shared test data not found"
fi

# Create necessary directories
mkdir -p logs screenshots results

echo "Setup complete for Project A!"
echo "To run tests: ./run_tests.sh"
echo "To start server manually: python server/server.py"