#!/bin/bash

echo "🚀 ElderWise AI Setup Script"
echo "=========================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "📋 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add:"
    echo "   1. Your Hugging Face token (HF_TOKEN)"
    echo "   2. Your Redis password (REDIS_PASSWORD)" 
    echo "   3. Your Pinecone API key (PINECONE_API_KEY)"
    echo ""
    echo "The MongoDB connection string is already configured."
    echo ""
    read -p "Press Enter after you've updated .env file..."
else
    echo "✅ .env file already exists"
fi

# Check Python version
echo ""
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1)
if [[ $? -eq 0 ]]; then
    echo "✅ $python_version"
else
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo ""
    echo "🔧 Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source .venv/bin/activate || . .venv/Scripts/activate 2>/dev/null

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run test setup
echo ""
echo "🧪 Running setup test..."
python test_setup.py

echo ""
echo "✨ Setup complete!"
echo ""
echo "To start the application:"
echo "  source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate"
echo "  python run.py"
echo ""
echo "Or for development mode:"
echo "  python -m uvicorn src.api.main:app --reload"