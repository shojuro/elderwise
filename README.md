# ElderWise AI

A persistent memory-driven AI companion designed to support elderly users with health tracking, emotional companionship, and proactive care logic.

## Overview

ElderWise is not just a chatbot—it's a foundational AI system with memory, context, and evolving intelligence. The system maintains persistent memory across interactions, allowing it to remember past conversations, track health information, and provide contextual, empathetic responses.

## Features

- **Persistent Memory**: 3-month active memory with 9-month archive
- **Multi-tier Storage**: Redis for sessions, MongoDB for structured data, Pinecone for semantic search
- **Context-Aware Responses**: Assembles relevant memories to provide continuity
- **Health & Emotion Tracking**: Automatically categorizes and tags interactions
- **Scheduled Memory Management**: Automatic archival and cleanup processes

## Tech Stack

- **AI Model**: Mistral 7B Instruct v0.3 (via Hugging Face)
- **Framework**: FastAPI
- **Databases**: 
  - Redis (session management)
  - MongoDB (user profiles & memory fragments)
  - Pinecone (vector embeddings)
- **Language**: Python 3.8+

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/elderwise.git
cd elderwise
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

## Configuration

Edit the `.env` file with your credentials:

- `HF_TOKEN`: Your Hugging Face API token with READ access
- `PINECONE_API_KEY`: Your Pinecone API key
- `MONGODB_URI`: MongoDB connection string
- `REDIS_HOST`, `REDIS_PORT`: Redis connection details

## Running the Application

### Development Mode

```bash
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
python run.py
```

## API Endpoints

### AI Interaction
- `POST /ai/respond` - Generate AI response with memory context
- `POST /ai/respond/stream` - Streaming response endpoint
- `GET /ai/validate` - Validate system components

### User Management
- `POST /users/create` - Create new user profile
- `GET /users/{user_id}` - Get user profile
- `PUT /users/{user_id}` - Update user profile
- `GET /users/{user_id}/stats` - Get user statistics

### Memory Management
- `POST /memory/create` - Create memory fragment
- `POST /memory/search` - Search memories semantically
- `GET /memory/{user_id}/recent` - Get recent memories
- `GET /memory/{user_id}/session` - Get session history
- `POST /memory/archive` - Trigger archival process

## Example Usage

### Creating a User
```bash
curl -X POST http://localhost:8000/users/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "name": "Margaret Thompson",
    "age": 84,
    "conditions": ["diabetes", "hypertension"],
    "interests": ["gardening", "jazz music"]
  }'
```

### Sending a Message
```bash
curl -X POST http://localhost:8000/ai/respond \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "I forgot to take my medication this morning"
  }'
```

## Memory Architecture

The system implements a sophisticated memory architecture:

1. **Short-term Memory** (Redis): Recent conversation turns
2. **Structured Memory** (MongoDB): User profiles, memory fragments, interaction logs
3. **Semantic Memory** (Pinecone): Vector embeddings for similarity search

Memory fragments are automatically categorized as:
- `health`: Medical-related conversations
- `emotion`: Emotional states and feelings
- `event`: Specific events or occurrences
- `preference`: User preferences and interests
- `interaction`: General conversations

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
flake8 src/
```

### Type Checking
```bash
mypy src/
```

## Architecture

```
src/
├── api/              # FastAPI application and routes
├── memory/           # Memory management components
├── models/           # Pydantic models
├── utils/            # Utilities (database, inference, etc.)
└── config/           # Configuration management
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions, please open a GitHub issue or contact the team.