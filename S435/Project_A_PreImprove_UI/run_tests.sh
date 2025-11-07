#!/bin/bash
set -e
PORT=${1:-8000}
REPEAT=${2:-3}

# start static server in background
python server/server.py --port $PORT &
SERVER_PID=$!

# wait for server
sleep 1

python -m pytest tests/test_pre_ui.py -- --port $PORT --repeat $REPEAT

# move results to aggregated results folder
cp results/results_pre.json ../results/results_pre.json || true

# stop server
kill $SERVER_PID || true
