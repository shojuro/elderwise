#!/bin/bash

# ElderWise Basic Service Verification Script
# Checks if required services are running without Python dependencies

echo "============================================"
echo "ElderWise Basic Service Verification"
echo "============================================"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check function
check_service() {
    local service_name=$1
    local check_command=$2
    local success_message=$3
    local fail_message=$4
    
    echo -n "Checking $service_name... "
    if eval $check_command &> /dev/null; then
        echo -e "${GREEN}✓ OK${NC} - $success_message"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} - $fail_message"
        return 1
    fi
}

# Load .env file if it exists
if [ -f .env ]; then
    echo -e "${YELLOW}Loading .env file...${NC}"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${RED}Warning: .env file not found${NC}"
fi

echo ""
echo "Service Checks:"
echo "---------------"

# Check Redis
check_service "Redis" "redis-cli ping" "Redis is running" "Redis is not running. Start with: redis-server"

# Check MongoDB
check_service "MongoDB" "mongosh --eval 'db.runCommand({ping: 1})' --quiet" "MongoDB is running" "MongoDB is not running. Start with: mongod"

# Check if required environment variables are set
echo ""
echo "Environment Variables:"
echo "---------------------"

check_env_var() {
    local var_name=$1
    local var_value=${!var_name}
    
    if [ -z "$var_value" ] || [[ "$var_value" == *"your_"*"_here"* ]]; then
        echo -e "${RED}✗${NC} $var_name: Not configured"
        return 1
    else
        echo -e "${GREEN}✓${NC} $var_name: Configured"
        return 0
    fi
}

check_env_var "HF_TOKEN"
check_env_var "PINECONE_API_KEY"
check_env_var "MONGODB_URI"
check_env_var "REDIS_HOST"

# Check Python dependencies
echo ""
echo "Python Environment:"
echo "------------------"

if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} Python3 is installed: $(python3 --version)"
    
    # Check if we're in a virtual environment
    if [ -n "$VIRTUAL_ENV" ]; then
        echo -e "${GREEN}✓${NC} Virtual environment active: $VIRTUAL_ENV"
    else
        echo -e "${YELLOW}!${NC} No virtual environment active. Consider using: python3 -m venv venv"
    fi
    
    # Check for requirements.txt
    if [ -f requirements.txt ]; then
        echo -e "${GREEN}✓${NC} requirements.txt found"
        echo "   To install dependencies: pip install -r requirements.txt"
    else
        echo -e "${RED}✗${NC} requirements.txt not found"
    fi
else
    echo -e "${RED}✗${NC} Python3 is not installed"
fi

# Check Node.js for frontend
echo ""
echo "Frontend Environment:"
echo "--------------------"

if command -v node &> /dev/null; then
    echo -e "${GREEN}✓${NC} Node.js is installed: $(node --version)"
    
    if [ -f frontend/package.json ]; then
        echo -e "${GREEN}✓${NC} frontend/package.json found"
        echo "   To install dependencies: cd frontend && npm install"
    fi
else
    echo -e "${RED}✗${NC} Node.js is not installed"
fi

echo ""
echo "============================================"
echo "Next Steps:"
echo "1. Update .env file with your API keys"
echo "2. Install Python dependencies: pip install -r requirements.txt"
echo "3. Install frontend dependencies: cd frontend && npm install"
echo "4. Start services that are not running"
echo "5. Run the Python verification script for detailed checks"
echo "============================================"