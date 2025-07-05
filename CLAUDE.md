# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
ElderWise is a dual-architecture AI companion system for elderly care:
- **Main ElderWise**: Memory-driven FastAPI backend with React frontend
- **CleoAI subdirectory**: Extended implementation with advanced AI features

The system uses Mistral 7B LLM via Hugging Face with sophisticated multi-tier memory management for persistent, context-aware conversations.

## Architecture

### Memory System (Core Innovation)
The memory architecture is the heart of ElderWise, implementing a three-tier system:

1. **Session Memory** (Redis): Last N interactions, 24-hour TTL
2. **Structured Memory** (MongoDB): User profiles, memory fragments, interaction logs
3. **Semantic Memory** (Pinecone): Vector embeddings for similarity search

Memory flows through `MemoryController` which:
- Assembles context from all three tiers
- Classifies interactions (health, emotion, event, preference)
- Stores significant interactions across all tiers
- Handles archival (active → archive after 90 days)

### AI Abstraction Layer
Located in `src/ai/`, provides provider-agnostic interface:
- Primary: Mistral via Hugging Face
- Fallback: CleoAI (if subdirectory service running)
- Mock provider for testing

### Frontend Architecture
React 19 with TypeScript, featuring:
- Accessibility-first design (WCAG AA compliant)
- Voice interaction support (Web Speech API)
- PWA capabilities with offline support
- Tailwind CSS with elder-friendly design tokens

## Development Commands

### Backend
```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run development server
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Run specific tests
pytest tests/unit/test_memory_controller.py -v
pytest tests/unit/test_api_ai_routes.py::TestAIRoutes::test_generate_response_success

# Run test categories
./run_tests.sh --unit
./run_tests.sh --memory
./run_tests.sh --api

# Verify services
./verify_services_basic.sh
python3 verify_services.py  # Detailed check
```

### Frontend
```bash
cd frontend
npm install

# Development
npm run dev

# Run specific test suites
npm run test:components
npm run test:hooks
npm run test:a11y

# Watch mode for TDD
npm run test:watch
```

## Key Implementation Details

### Context Assembly (`src/memory/controller.py`)
```python
assemble_context() → {
    "user_profile": MongoDB data,
    "recent_interactions": Redis session,
    "relevant_memories": Pinecone semantic search,
    "recent_fragments": MongoDB recent memories,
    "context_string": Formatted for LLM
}
```

### Memory Classification
- **Significant interactions**: Keywords + length heuristics
- **Auto-tagging**: Health, emotion, daily, memory tags
- **Retention**: "active" (0-90 days) → "archive" (90-365 days)

### API Response Flow
1. User message → `MemoryController.assemble_context()`
2. Context → AI provider (with fallback chain)
3. Response → Background task stores to all memory tiers
4. Session ID maintained for conversation continuity

### Testing Strategy
- **Unit tests**: Mocked external services
- **Integration tests**: Complete user flows
- **API tests**: All endpoints with error cases
- **Component tests**: Isolated React components
- **Accessibility tests**: WCAG compliance

## Environment Variables
Required in `.env`:
- `HF_TOKEN`: Hugging Face API token
- `PINECONE_API_KEY`: Pinecone API key
- `MONGODB_URI`: MongoDB connection
- `REDIS_HOST`, `REDIS_PORT`: Redis connection

## API Endpoints
- `POST /ai/respond`: Main chat (returns session_id)
- `POST /ai/respond/stream`: SSE streaming
- `GET /users/{user_id}`: User profile
- `POST /memory/search`: Semantic memory search
- `GET /memory/{user_id}/recent`: Recent memories
- `POST /memory/archive`: Manual archival trigger

## Common Development Tasks

### Adding a New Memory Type
1. Update `MemoryFragment.type` pattern in `src/models/memory.py`
2. Add classification logic in `MemoryController._classify_interaction_type()`
3. Update tag extraction in `MemoryController._extract_tags()`
4. Add tests in `test_memory_controller.py`

### Implementing a New AI Provider
1. Create provider class in `src/ai/providers/`
2. Implement `AIProvider` interface
3. Add to provider factory in `src/ai/client.py`
4. Update `AI_PROVIDER` settings options

### Adding a Frontend Feature
1. Create component in appropriate directory
2. Add accessibility attributes (aria-label, role)
3. Implement responsive design (min-h-[48px] for touch)
4. Add component tests with accessibility checks
5. Update relevant hooks if needed

## Performance Considerations
- Memory context limited to top 5 semantic matches
- Session history trimmed to last N interactions (configurable)
- Background tasks for non-blocking storage operations
- Streaming responses for perceived performance

## Security Notes
- API keys loaded from environment only
- User IDs validated on all endpoints
- Memory access scoped to user
- No PII in logs

## Version Control Guidelines

### Branch Structure
- **Main branch**: `main` (protected, production-ready)
- **Feature branches**: `feature/<ticket>-<description>` (e.g., `feature/EW-123-voice-input`)
- **Release branches**: `release/v<major>.<minor>.<patch>` (e.g., `release/v1.2.0`)
- **Hotfix branches**: `hotfix/<ticket>-<description>` (e.g., `hotfix/EW-456-memory-leak`)

### Commit Messages
Follow conventional commits format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `security`

Example:
```
feat(memory): add automatic memory archival

Implement scheduled job to archive memories older than 90 days.
Archives are moved to separate collection with reduced indexing.

Closes #EW-123
```

### Pull Request Process
1. Create feature branch from latest `main`
2. Make changes following coding standards
3. Ensure all tests pass (`./run_tests.sh` and `npm test`)
4. Update documentation if needed
5. Create PR with description template
6. Address review feedback
7. Squash and merge to main

### Code Review Requirements
- At least 1 approval required
- All CI checks must pass
- No merge conflicts
- Test coverage maintained above 80%
- Security scan passing

### Release Process
1. Create release branch from main
2. Update version in `pyproject.toml` and `package.json`
3. Update CHANGELOG.md
4. Create PR to main
5. After merge, tag release: `git tag -a v1.2.0 -m "Release v1.2.0"`
6. Push tag: `git push origin v1.2.0`

### Hotfix Process
1. Create hotfix branch from latest production tag
2. Apply minimal fix
3. Test thoroughly
4. Create PR to main with expedited review
5. After merge, cherry-pick to current release branch if exists
6. Tag hotfix: `v1.2.1`

### Git Configuration
```bash
# Required setup
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global init.defaultBranch main
git config --global pull.rebase true

# Recommended aliases
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.st status
git config --global alias.unstage 'reset HEAD --'
```