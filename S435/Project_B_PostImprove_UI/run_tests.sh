#!/bin/bash
set -e
PORT=${1:-8001}
REPEAT=${2:-3}

python server/server.py --port $PORT &
SERVER_PID=$!

sleep 1
python -m pytest tests/test_post_ui.py -- --port $PORT --repeat $REPEAT

cp results/results_post.json ../results/results_post.json || true

kill $SERVER_PID || true
