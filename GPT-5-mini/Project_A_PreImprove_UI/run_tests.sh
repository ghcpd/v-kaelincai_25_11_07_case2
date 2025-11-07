#!/usr/bin/env bash
set -e
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export SIM_LATENCY_MS=${1:-0}
python server/server.py &
SERVER_PID=$!
sleep 1
pytest tests -q --capture=tee-sys
kill $SERVER_PID || true
