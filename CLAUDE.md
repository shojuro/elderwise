# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
ElderWise is a memory-driven AI companion system designed for elderly care support. It provides persistent memory, health tracking, and empathetic conversation capabilities using Mistral 7B LLM with a sophisticated multi-tier memory architecture.

## Architecture
- **src/api/**: FastAPI application and REST endpoints
- **src/memory/**: Memory management (controller, session, storage, semantic)
- **src/models/**: Pydantic data models
- **src/utils/**: Utilities (database connections, inference, scheduler)
- **src/config/**: Configuration management

## Key Components
1. **Memory Controller**: Assembles context from Redis (sessions), MongoDB (structured data), and Pinecone (semantic search)
2. **Inference Service**: Integrates Mistral 7B via Hugging Face API
3. **Scheduled Jobs**: Automatic memory archival and cleanup
4. **API Endpoints**: RESTful interface for AI interactions, user management, and memory operations

## Development Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Run production server
python run.py

# Test setup
python test_setup.py

# Format code
black src/
flake8 src/

# Run tests
pytest tests/
```

## Environment Setup
1. Copy `.env.example` to `.env`
2. Required environment variables:
   - HF_TOKEN: Hugging Face API token
   - PINECONE_API_KEY: Pinecone vector database key
   - MONGODB_URI: MongoDB connection string
   - Redis configuration

## API Structure
- `/ai/respond` - Main chat endpoint with memory
- `/users/*` - User profile management
- `/memory/*` - Memory operations and search
- `/health` - System health check

## Memory Architecture
- **Active Memory**: 0-3 months (fast access)
- **Archive Memory**: 3-12 months (background queries)
- **Session Memory**: Last N interactions (Redis)
- **Semantic Memory**: Vector embeddings (Pinecone)

## Testing Approach
- Unit tests for individual components
- Integration tests for memory pipeline
- API endpoint tests
- Mock external services (HF, Pinecone) for testing