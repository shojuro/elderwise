#!/bin/bash

# Frontend Test Runner Script

echo "============================================"
echo "ElderWise Frontend Test Suite"
echo "============================================"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the frontend directory
if [ ! -f "package.json" ] || [ ! -d "src" ]; then
    echo -e "${YELLOW}Warning: This script should be run from the frontend directory${NC}"
    echo "Current directory: $(pwd)"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}node_modules not found. Installing dependencies...${NC}"
    npm install
fi

# Parse command line arguments
TEST_TYPE="all"
WATCH=""
UI=""
COVERAGE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --components)
            TEST_TYPE="components"
            shift
            ;;
        --hooks)
            TEST_TYPE="hooks"
            shift
            ;;
        --a11y)
            TEST_TYPE="a11y"
            shift
            ;;
        --watch)
            WATCH="--watch"
            shift
            ;;
        --ui)
            UI="--ui"
            shift
            ;;
        --coverage)
            COVERAGE="--coverage"
            shift
            ;;
        -h|--help)
            echo "Usage: ./run-tests.sh [options]"
            echo ""
            echo "Options:"
            echo "  --components    Run only component tests"
            echo "  --hooks         Run only hook tests"
            echo "  --a11y          Run only accessibility tests"
            echo "  --watch         Run tests in watch mode"
            echo "  --ui            Open Vitest UI"
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
CMD="npm run"

if [ ! -z "$UI" ]; then
    echo -e "${BLUE}Opening Vitest UI...${NC}"
    CMD="$CMD test:ui"
elif [ ! -z "$WATCH" ]; then
    echo -e "${BLUE}Running tests in watch mode...${NC}"
    CMD="$CMD test:watch"
elif [ ! -z "$COVERAGE" ]; then
    echo -e "${BLUE}Running tests with coverage...${NC}"
    CMD="$CMD test:coverage"
else
    case $TEST_TYPE in
        components)
            echo -e "${BLUE}Running component tests...${NC}"
            CMD="$CMD test:components"
            ;;
        hooks)
            echo -e "${BLUE}Running hook tests...${NC}"
            CMD="$CMD test:hooks"
            ;;
        a11y)
            echo -e "${BLUE}Running accessibility tests...${NC}"
            CMD="$CMD test:a11y"
            ;;
        all)
            echo -e "${BLUE}Running all tests...${NC}"
            CMD="$CMD test"
            ;;
    esac
fi

echo "Command: $CMD"
echo "============================================"

# Run tests
if $CMD; then
    echo ""
    echo -e "${GREEN}✓ All tests passed!${NC}"
    
    if [ ! -z "$COVERAGE" ]; then
        echo ""
        echo -e "${BLUE}Coverage report generated in coverage/index.html${NC}"
    fi
else
    echo ""
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi

echo "============================================"