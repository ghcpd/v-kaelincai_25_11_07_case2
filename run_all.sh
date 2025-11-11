#!/bin/bash
# Master script to run both projects and generate comparison report

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Default values
NETWORK_DELAY=0
REPEAT=1
TEST_DATA="test_data.json"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
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

echo "=========================================="
echo "UI/UX Improvement Evaluation"
echo "=========================================="
echo "Network delay: ${NETWORK_DELAY}ms"
echo "Repeat count: $REPEAT"
echo "Test data: $TEST_DATA"
echo ""

# Create results directory
mkdir -p results

# Run Project A (Pre-Improvement)
echo "=========================================="
echo "Running Project A (Pre-Improvement)..."
echo "=========================================="
cd Project_A_PreImprove_UI
bash run_tests.sh --port 8000 --network-delay "$NETWORK_DELAY" --repeat "$REPEAT" --test-data "../$TEST_DATA"
cd ..

# Run Project B (Post-Improvement)
echo ""
echo "=========================================="
echo "Running Project B (Post-Improvement)..."
echo "=========================================="
cd Project_B_PostImprove_UI
bash run_tests.sh --port 8001 --network-delay "$NETWORK_DELAY" --repeat "$REPEAT" --test-data "../$TEST_DATA"
cd ..

# Generate comparison report
echo ""
echo "=========================================="
echo "Generating comparison report..."
echo "=========================================="
python generate_compare_report.py --test-data "$TEST_DATA"

echo ""
echo "=========================================="
echo "Evaluation complete!"
echo "=========================================="
echo "Results saved in: results/"
echo "Comparison report: compare_report.md"
echo ""

