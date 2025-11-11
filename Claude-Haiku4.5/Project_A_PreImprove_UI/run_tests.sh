#!/bin/bash
# Test execution script for Project A - Pre-improvement UI

set -e  # Exit on any error

echo "================================"
echo "Project A - Pre-improvement UI Tests"
echo "================================"

# Configuration
REPEAT_COUNT=${1:-1}
NETWORK_LATENCY=${2:-100}
HEADLESS=${3:-false}

echo "Configuration:"
echo "  Repeat count: $REPEAT_COUNT"
echo "  Network latency: ${NETWORK_LATENCY}ms"
echo "  Headless mode: $HEADLESS"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    bash setup.sh
fi

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/Mac
    source venv/bin/activate
fi

# Ensure test data is available
if [ ! -f "data/test_data.json" ]; then
    if [ -f "../test_data.json" ]; then
        echo "Copying test data..."
        cp ../test_data.json data/
    else
        echo "Error: Test data file not found!"
        exit 1
    fi
fi

# Create logs directory with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="logs/log_pre_${TIMESTAMP}.txt"

echo "Starting tests..."
echo "Log file: $LOG_FILE"

# Set environment variables
export REPEAT_COUNT=$REPEAT_COUNT
export NETWORK_LATENCY=$NETWORK_LATENCY
export HEADLESS=$HEADLESS

# Function to run tests
run_tests() {
    local attempt=$1
    echo ""
    echo "Test run $attempt of $REPEAT_COUNT"
    echo "--------------------------------"
    
    # Run the test harness
    python tests/test_pre_ui.py 2>&1 | tee -a "$LOG_FILE"
    
    local exit_code=${PIPESTATUS[0]}
    
    if [ $exit_code -eq 0 ]; then
        echo "Test run $attempt: PASSED"
    else
        echo "Test run $attempt: FAILED (exit code: $exit_code)"
        return $exit_code
    fi
    
    return 0
}

# Run tests multiple times if specified
total_passed=0
total_failed=0

for ((i=1; i<=REPEAT_COUNT; i++)); do
    if run_tests $i; then
        ((total_passed++))
    else
        ((total_failed++))
    fi
done

# Aggregate results if multiple runs
if [ $REPEAT_COUNT -gt 1 ]; then
    echo ""
    echo "================================"
    echo "AGGREGATE TEST RESULTS"
    echo "================================"
    echo "Total runs: $REPEAT_COUNT"
    echo "Passed: $total_passed"
    echo "Failed: $total_failed"
    echo "Success rate: $(echo "scale=1; $total_passed * 100 / $REPEAT_COUNT" | bc -l)%"
    
    # Create aggregated results file
    AGGREGATED_RESULTS="results/aggregated_results_pre_${TIMESTAMP}.json"
    cat > "$AGGREGATED_RESULTS" << EOF
{
  "project": "Project_A_PreImprove_UI",
  "version": "pre-improvement",
  "timestamp": "$(date -Iseconds)",
  "configuration": {
    "repeat_count": $REPEAT_COUNT,
    "network_latency_ms": $NETWORK_LATENCY,
    "headless": $HEADLESS
  },
  "summary": {
    "total_runs": $REPEAT_COUNT,
    "passed": $total_passed,
    "failed": $total_failed,
    "success_rate": $(echo "scale=3; $total_passed * 100 / $REPEAT_COUNT" | bc -l)
  },
  "log_file": "$LOG_FILE"
}
EOF
    echo "Aggregated results saved to: $AGGREGATED_RESULTS"
fi

# Check if any tests failed
if [ $total_failed -gt 0 ]; then
    echo ""
    echo "❌ Some tests failed. Check the log file for details: $LOG_FILE"
    exit 1
else
    echo ""
    echo "✅ All tests passed successfully!"
fi

echo ""
echo "Test artifacts:"
echo "  Results: $(ls results/results_pre*.json 2>/dev/null | tail -1 || echo 'None')"
echo "  Screenshots: screenshots/"
echo "  Logs: $LOG_FILE"
echo ""
echo "To view results:"
echo "  cat results/results_pre*.json | jq ."
echo ""