#!/bin/bash
# Setup script for Project B - Post-improvement UI

echo "Setting up Project B - Post-improvement UI environment..."

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

# Create expected results template
echo "Creating expected results template..."
cat > data/expected_post.json << 'EOF'
{
  "improvements": {
    "modal_load_time_reduction_percent": 60,
    "time_to_title_visible_reduction_percent": 80,
    "task_creation_time_reduction_percent": 25,
    "first_field_visibility_percent": 100,
    "lazy_loading_functional": true,
    "progressive_loading_functional": true
  },
  "target_metrics": {
    "modal_load_ms_max": 150,
    "time_to_title_visible_ms_max": 100,
    "task_create_ms_max": 6000,
    "accessibility_score_min": 0.9
  }
}
EOF

# Create necessary directories
mkdir -p logs screenshots results

echo "Setup complete for Project B!"
echo "To run tests: ./run_tests.sh"
echo "To start server manually: python server/server.py"