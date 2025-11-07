#!/bin/bash
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
python -m playwright install

# note: on Windows users should use the PowerShell equivalent commands
# For Powershell: python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt; python -m playwright install
