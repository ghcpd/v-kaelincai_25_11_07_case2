#!/usr/bin/env bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install
# start server
python server/server.py &
server_pid=$!
sleep 1
python tests/test_pre_ui.py
kill $server_pid
