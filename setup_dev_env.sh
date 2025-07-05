#!/bin/bash

# ElderWise Development Environment Setup Script

echo "============================================"
echo "ElderWise Development Environment Setup"
echo "============================================"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to prompt user
prompt_yes_no() {
    local prompt=$1
    local response
    read -p "$prompt (y/n): " response
    [[ "$response" =~ ^[Yy]$ ]]
}

# 1. Check Python and create virtual environment
echo -e "\n${BLUE}Step 1: Python Environment${NC}"
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} Python3 found: $(python3 --version)"
    
    if [ ! -d "venv" ]; then
        if prompt_yes_no "Create virtual environment?"; then
            python3 -m venv venv
            echo -e "${GREEN}✓${NC} Virtual environment created"
        fi
    else
        echo -e "${GREEN}✓${NC} Virtual environment already exists"
    fi
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        echo "To activate the virtual environment, run:"
        echo -e "${YELLOW}source venv/bin/activate${NC}"
    fi
else
    echo -e "${RED}✗${NC} Python3 not found. Please install Python 3.8+"
fi

# 2. Install Python dependencies
echo -e "\n${BLUE}Step 2: Python Dependencies${NC}"
if [ -f "requirements.txt" ]; then
    echo "To install Python dependencies, run:"
    echo -e "${YELLOW}pip install -r requirements.txt${NC}"
else
    echo -e "${RED}✗${NC} requirements.txt not found"
fi

# 3. Install Frontend dependencies
echo -e "\n${BLUE}Step 3: Frontend Dependencies${NC}"
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    echo "To install frontend dependencies, run:"
    echo -e "${YELLOW}cd frontend && npm install${NC}"
else
    echo -e "${RED}✗${NC} frontend/package.json not found"
fi

# 4. Service startup commands
echo -e "\n${BLUE}Step 4: Start Required Services${NC}"
echo "To start the required services:"
echo -e "${YELLOW}1. Redis:${NC} redis-server"
echo -e "${YELLOW}2. MongoDB:${NC} mongod"

# 5. Environment configuration
echo -e "\n${BLUE}Step 5: Environment Configuration${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    echo "Make sure to update the following in your .env file:"
    echo "  - HF_TOKEN: Your Hugging Face API token"
    echo "  - PINECONE_API_KEY: Your Pinecone API key"
else
    echo -e "${RED}✗${NC} .env file not found"
fi

# 6. Create Pinecone index setup script
echo -e "\n${BLUE}Step 6: Pinecone Index Setup${NC}"
cat > setup_pinecone_index.py << 'EOF'
#!/usr/bin/env python3
"""Create Pinecone index for ElderWise"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME", "elderwise-memory")

if not api_key or api_key == "your_pinecone_api_key_here":
    print("Error: Please set PINECONE_API_KEY in your .env file")
    exit(1)

pc = Pinecone(api_key=api_key)

# Check if index exists
existing_indexes = [idx.name for idx in pc.list_indexes()]

if index_name not in existing_indexes:
    print(f"Creating index '{index_name}'...")
    pc.create_index(
        name=index_name,
        dimension=768,  # For sentence-transformers/all-MiniLM-L6-v2
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-west-2"
        )
    )
    print(f"✓ Index '{index_name}' created successfully")
else:
    print(f"✓ Index '{index_name}' already exists")

EOF

echo "Created setup_pinecone_index.py"
echo "To create the Pinecone index, run:"
echo -e "${YELLOW}python3 setup_pinecone_index.py${NC}"

# 7. Quick start commands
echo -e "\n${BLUE}Quick Start Commands:${NC}"
echo "============================================"
echo "# Backend setup"
echo "source venv/bin/activate"
echo "pip install -r requirements.txt"
echo "python3 setup_pinecone_index.py"
echo ""
echo "# Frontend setup"
echo "cd frontend && npm install"
echo ""
echo "# Start services"
echo "redis-server"
echo "mongod"
echo ""
echo "# Run the application"
echo "python -m uvicorn src.api.main:app --reload"
echo "cd frontend && npm run dev"
echo "============================================"

echo -e "\n${GREEN}Setup script complete!${NC}"