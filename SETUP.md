# ElderWise Development Setup Guide

## Prerequisites

Before setting up ElderWise, ensure you have the following installed:

- **Python 3.8+** - Backend runtime
- **Node.js 16+** - Frontend build tool
- **Redis** - Session storage and caching
- **MongoDB** - Primary data storage
- **Git** - Version control

## Quick Start

1. **Clone and enter the repository**
   ```bash
   git clone <repository-url>
   cd ElderWise
   ```

2. **Run the setup script**
   ```bash
   chmod +x setup_dev_env.sh
   ./setup_dev_env.sh
   ```

## Manual Setup Steps

### 1. Environment Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Update the `.env` file with your credentials:
   - `HF_TOKEN`: Get from [Hugging Face](https://huggingface.co/settings/tokens)
   - `PINECONE_API_KEY`: Get from [Pinecone Console](https://console.pinecone.io/)

### 2. Backend Setup

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create the Pinecone index:
   ```bash
   python3 setup_pinecone_index.py
   ```

### 3. Frontend Setup

1. Install Node.js dependencies:
   ```bash
   cd frontend
   npm install
   ```

### 4. Start Required Services

1. **Redis** (in a separate terminal):
   ```bash
   redis-server
   ```

2. **MongoDB** (in a separate terminal):
   ```bash
   mongod
   ```

### 5. Run the Application

1. **Backend API** (from project root):
   ```bash
   python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend** (in a separate terminal):
   ```bash
   cd frontend
   npm run dev
   ```

## Verification

1. Run the basic verification script:
   ```bash
   ./verify_services_basic.sh
   ```

2. For detailed verification (requires dependencies):
   ```bash
   python3 verify_services.py
   ```

## Service URLs

Once running, access the application at:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Troubleshooting

### Redis Connection Error
- Ensure Redis is installed: `sudo apt install redis` (Ubuntu/Debian) or `brew install redis` (macOS)
- Check if Redis is running: `redis-cli ping` (should return "PONG")

### MongoDB Connection Error
- Ensure MongoDB is installed: Follow [MongoDB installation guide](https://docs.mongodb.com/manual/installation/)
- Check if MongoDB is running: `mongosh --eval "db.runCommand({ping: 1})"`

### Pinecone Index Error
- Verify your API key is correct in `.env`
- Check your Pinecone dashboard for quota limits
- Ensure the index name matches in `.env` and Pinecone console

### Hugging Face Token Error
- Ensure your token has "read" permissions for model access
- Verify the token in your [Hugging Face settings](https://huggingface.co/settings/tokens)

### Module Import Errors
- Ensure you've activated the virtual environment
- Try reinstalling dependencies: `pip install -r requirements.txt --force-reinstall`

## Development Workflow

1. Always activate the virtual environment before working:
   ```bash
   source venv/bin/activate
   ```

2. Run tests before committing:
   ```bash
   pytest tests/
   ```

3. Format code:
   ```bash
   black src/
   flake8 src/
   ```

4. Check frontend linting:
   ```bash
   cd frontend
   npm run lint
   ```

## Next Steps

- Review the [API documentation](http://localhost:8000/docs) for available endpoints
- Check `CLAUDE.md` for AI development guidelines
- Explore the memory architecture in `src/memory/`
- Test the chat interface at http://localhost:5173