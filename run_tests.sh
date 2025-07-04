#!/bin/bash

# ElderWise Test Runner Script

echo "============================================"
echo "ElderWise Test Suite"
echo "============================================"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Warning: No virtual environment active${NC}"
    echo "Consider activating with: source venv/bin/activate"
    echo ""
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest not found${NC}"
    echo "Install with: pip install pytest pytest-asyncio pytest-mock"
    exit 1
fi

# Parse command line arguments
TEST_TYPE="all"
VERBOSE=""
COVERAGE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --unit)
            TEST_TYPE="unit"
            shift
            ;;
        --integration)
            TEST_TYPE="integration"
            shift
            ;;
        --memory)
            TEST_TYPE="memory"
            shift
            ;;
        --api)
            TEST_TYPE="api"
            shift
            ;;
        -v|--verbose)
            VERBOSE="-vv"
            shift
            ;;
        --coverage)
            COVERAGE="--cov=src --cov-report=html --cov-report=term"
            shift
            ;;
        -h|--help)
            echo "Usage: ./run_tests.sh [options]"
            echo ""
            echo "Options:"
            echo "  --unit          Run only unit tests"
            echo "  --integration   Run only integration tests"
            echo "  --memory        Run only memory-related tests"
            echo "  --api           Run only API-related tests"
            echo "  -v, --verbose   Verbose output"
            echo "  --coverage      Generate coverage report"
            echo "  -h, --help      Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Build test command
CMD="pytest $VERBOSE $COVERAGE"

case $TEST_TYPE in
    unit)
        echo -e "${BLUE}Running unit tests...${NC}"
        CMD="$CMD tests/unit/ -m 'not integration'"
        ;;
    integration)
        echo -e "${BLUE}Running integration tests...${NC}"
        CMD="$CMD tests/unit/test_memory_integration.py"
        ;;
    memory)
        echo -e "${BLUE}Running memory tests...${NC}"
        CMD="$CMD tests/unit/test_memory_*.py tests/unit/test_session_*.py tests/unit/test_semantic_*.py"
        ;;
    api)
        echo -e "${BLUE}Running API tests...${NC}"
        CMD="$CMD tests/unit/test_api_*.py tests/integration/test_api_integration.py"
        ;;
    all)
        echo -e "${BLUE}Running all tests...${NC}"
        CMD="$CMD tests/"
        ;;
esac

echo "Command: $CMD"
echo "============================================"

# Run tests
if $CMD; then
    echo ""
    echo -e "${GREEN}✓ All tests passed!${NC}"
    
    if [ ! -z "$COVERAGE" ]; then
        echo ""
        echo -e "${BLUE}Coverage report generated in htmlcov/index.html${NC}"
    fi
else
    echo ""
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi

echo "============================================"