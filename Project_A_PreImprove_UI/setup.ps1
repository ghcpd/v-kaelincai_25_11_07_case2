# PowerShell setup script for Project A (Pre-Improvement) on Windows

Write-Host "Setting up Project A (Pre-Improvement)..."

# Create virtual environment
if (-not (Test-Path "venv")) {
    python -m venv venv
}

# Activate virtual environment
& "venv\Scripts\Activate.ps1"

# Install Python dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Create necessary directories
New-Item -ItemType Directory -Force -Path "screenshots" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "results" | Out-Null
New-Item -ItemType Directory -Force -Path "data" | Out-Null

Write-Host "Setup complete!"
Write-Host "To activate the virtual environment, run: .\venv\Scripts\Activate.ps1"

