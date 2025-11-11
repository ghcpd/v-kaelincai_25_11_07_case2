#!/bin/bash
# Run tests for Project A (Pre-Improvement)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Default values
PORT=8000
NETWORK_DELAY=0
REPEAT=1
TEST_DATA="data/test_data.json"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --network-delay)
            NETWORK_DELAY="$2"
            shift 2
            ;;
        --repeat)
            REPEAT="$2"
            shift 2
            ;;
        --test-data)
            TEST_DATA="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Starting Project A (Pre-Improvement) tests..."
echo "Port: $PORT"
echo "Network delay: ${NETWORK_DELAY}ms"
echo "Repeat count: $REPEAT"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start server in background
echo "Starting server on port $PORT..."
python server/server.py --port "$PORT" --network-delay "$NETWORK_DELAY" --test-data "$TEST_DATA" &
SERVER_PID=$!

# Wait for server to start
sleep 2

# Check if server is running
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "Failed to start server"
    exit 1
fi

echo "Server started (PID: $SERVER_PID)"

# Run tests
echo "Running tests..."
python tests/test_pre_ui.py --url "http://localhost:$PORT" --network-delay "$NETWORK_DELAY" --repeat "$REPEAT" --test-data "$TEST_DATA" || TEST_EXIT_CODE=$?

# Stop server
echo "Stopping server..."
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true

# Exit with test exit code
exit ${TEST_EXIT_CODE:-0}

