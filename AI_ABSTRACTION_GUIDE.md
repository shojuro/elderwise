# AI Abstraction Layer Guide

## Overview

ElderWise now includes a clean abstraction layer that allows seamless switching between different AI providers (Mistral, CleoAI, or Mock for testing). This guide explains how to use and extend the abstraction.

## Architecture

```
src/ai/
├── __init__.py          # Exports AIClient
├── base.py              # Abstract interfaces and data models
├── client.py            # AI Client factory with fallback support
└── providers/           # Provider implementations
    ├── __init__.py
    ├── mistral.py       # Mistral via HuggingFace
    ├── cleoai.py        # CleoAI via GraphQL/REST
    └── mock.py          # Mock provider for testing
```

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Primary AI provider (mistral, cleoai, or mock)
AI_PROVIDER=mistral

# Fallback providers (optional)
# AI_FALLBACK_PROVIDERS=["cleoai", "mock"]

# Provider-specific settings
MISTRAL_MODEL_ID=mistralai/Mistral-7B-Instruct-v0.3
# CLEOAI_ENDPOINT=http://localhost:8000
# CLEOAI_API_KEY=your_api_key_here
```

### Switching Providers

1. **Use Mistral (default)**:
   ```bash
   AI_PROVIDER=mistral
   ```

2. **Use CleoAI**:
   ```bash
   AI_PROVIDER=cleoai
   CLEOAI_ENDPOINT=http://your-cleoai-instance:8000
   CLEOAI_API_KEY=your_api_key
   ```

3. **Use Mock (for testing)**:
   ```bash
   AI_PROVIDER=mock
   ```

### Enabling Fallbacks

To enable automatic fallback when the primary provider fails:

```bash
AI_PROVIDER=cleoai
AI_FALLBACK_PROVIDERS=["mistral", "mock"]
```

## Usage Examples

### Basic Usage

```python
from src.ai.client import ai_client

# Initialize (happens automatically on first use)
await ai_client.initialize()

# Generate a response
response = await ai_client.generate_response(
    context="Hello, how are you feeling today?",
    temperature=0.7,
    max_tokens=500,
    user_id="user123"
)

if response.success:
    print(f"AI: {response.response}")
    print(f"Provider: {response.provider}")
    print(f"Response time: {response.response_time_ms}ms")
else:
    print(f"Error: {response.error}")
```

### Streaming Responses

```python
async for chunk in ai_client.generate_streaming_response(
    context="Tell me a story",
    temperature=0.8,
    max_tokens=1000
):
    print(chunk, end="", flush=True)
```

### Health Checks

```python
health = await ai_client.health_check()
print(f"Overall status: {health['overall_status']}")
print(f"Primary provider: {health['primary_provider']['status']}")
```

## Adding a New Provider

1. Create a new provider in `src/ai/providers/new_provider.py`:

```python
from src.ai.base import AIProviderInterface, AIRequest, AIResponse, AIProvider

class NewProvider(AIProviderInterface):
    async def initialize(self) -> None:
        # Setup connection
        pass
    
    async def generate_response(self, request: AIRequest) -> AIResponse:
        # Generate response
        pass
    
    async def generate_streaming_response(self, request: AIRequest):
        # Stream response
        pass
    
    async def validate_connection(self) -> bool:
        # Validate provider is accessible
        pass
    
    async def get_model_info(self) -> Dict[str, Any]:
        # Return model information
        pass
```

2. Register in `src/ai/client.py`:

```python
PROVIDERS = {
    AIProvider.MISTRAL: MistralProvider,
    AIProvider.CLEOAI: CleoAIProvider,
    AIProvider.MOCK: MockProvider,
    AIProvider.NEW: NewProvider  # Add here
}
```

3. Add to `src/ai/base.py`:

```python
class AIProvider(str, Enum):
    MISTRAL = "mistral"
    CLEOAI = "cleoai"
    MOCK = "mock"
    NEW = "new"  # Add here
```

4. Add configuration handling in `AIClient._get_provider_config()`.

## Testing

Run the AI abstraction tests:

```bash
pytest tests/unit/ai/test_ai_client.py -v
```

Test with different providers:

```bash
# Test with mock provider
AI_PROVIDER=mock python test_setup.py

# Test with CleoAI
AI_PROVIDER=cleoai python test_setup.py
```

## Migration from Direct Inference

The API routes have been updated to use the abstraction. Old code:

```python
response_data = await mistral_inference.generate_response(...)
```

New code:

```python
response_data = await ai_client.generate_response(...)
```

## Benefits

1. **Provider Flexibility**: Switch between AI providers without code changes
2. **Automatic Fallback**: Resilience when primary provider fails
3. **Consistent Interface**: Same API regardless of provider
4. **Easy Testing**: Mock provider for unit tests
5. **Future-Proof**: Easy to add new providers (GPT-4, Claude, etc.)

## Monitoring

The health check endpoint now includes AI provider status:

```bash
curl http://localhost:8000/ai/validate
```

Response includes:
- AI client health
- Provider status
- Fallback availability
- Model information