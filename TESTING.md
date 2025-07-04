# ElderWise Testing Guide

## Overview

ElderWise has comprehensive test coverage across both backend (Python/FastAPI) and frontend (React/TypeScript) components. This guide explains the testing strategy, how to run tests, and how to write new tests.

## Test Structure

### Backend Tests (`/tests/`)

```
tests/
├── __init__.py
├── conftest.py           # Shared fixtures and configuration
├── unit/                 # Unit tests
│   ├── test_memory_controller.py
│   ├── test_session_manager.py
│   ├── test_memory_storage.py
│   ├── test_semantic_memory.py
│   ├── test_memory_integration.py
│   ├── test_api_main.py
│   ├── test_api_ai_routes.py
│   ├── test_api_user_routes.py
│   └── test_api_memory_routes.py
└── integration/          # Integration tests
    └── test_api_integration.py
```

### Frontend Tests (`/src/__tests__/`)

```
src/__tests__/
├── components/           # Component tests
│   ├── common/
│   │   ├── Button.test.tsx
│   │   ├── Modal.test.tsx
│   │   └── Layout.test.tsx
│   └── chat/
│       ├── ChatMessage.test.tsx
│       └── ChatInput.test.tsx
├── hooks/               # Hook tests
│   └── useChat.test.ts
├── accessibility.test.tsx
├── test-utils.tsx       # Test utilities and helpers
└── setupTests.ts        # Test setup and mocks
```

## Running Tests

### Backend Tests

```bash
# Run all tests
./run_tests.sh

# Run specific test types
./run_tests.sh --unit          # Unit tests only
./run_tests.sh --integration   # Integration tests only
./run_tests.sh --memory        # Memory-related tests only
./run_tests.sh --api           # API tests only

# Additional options
./run_tests.sh -v              # Verbose output
./run_tests.sh --coverage      # Generate coverage report
```

### Frontend Tests

```bash
cd frontend

# Run all tests
./run-tests.sh

# Run specific test types
./run-tests.sh --components    # Component tests only
./run-tests.sh --hooks         # Hook tests only
./run-tests.sh --a11y          # Accessibility tests only

# Additional options
./run-tests.sh --watch         # Run in watch mode
./run-tests.sh --ui            # Open Vitest UI
./run-tests.sh --coverage      # Generate coverage report
```

## Test Coverage Areas

### Backend Coverage

1. **Memory Management**
   - Memory Controller: Context assembly, interaction storage, classification
   - Session Manager: Redis operations, session history
   - Memory Storage: MongoDB CRUD operations, archival
   - Semantic Memory: Vector operations, search functionality

2. **API Endpoints**
   - Health checks and lifecycle management
   - AI chat endpoints (sync and streaming)
   - User management (CRUD operations)
   - Memory operations (create, search, archive)

3. **Integration Tests**
   - Complete user flows
   - Memory lifecycle management
   - Error propagation

### Frontend Coverage

1. **Components**
   - Common components (Button, Modal, Layout)
   - Chat components (Message display, Input handling)
   - Accessibility compliance

2. **Hooks**
   - Chat functionality
   - Voice interaction
   - State management

3. **Accessibility**
   - WCAG compliance
   - Keyboard navigation
   - Screen reader support

## Writing Tests

### Backend Test Example

```python
import pytest
from unittest.mock import AsyncMock
from src.memory.controller import MemoryController

@pytest.mark.asyncio
async def test_assemble_context(memory_controller):
    # Arrange
    mock_profile = UserProfile(user_id="test", name="Test User")
    memory_controller.storage.get_user_profile = AsyncMock(return_value=mock_profile)
    
    # Act
    context = await memory_controller.assemble_context("test", "Hello")
    
    # Assert
    assert context["user_profile"]["name"] == "Test User"
    assert "Hello" in context["context_string"]
```

### Frontend Test Example

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '../../../components/common/Button';

describe('Button Component', () => {
  it('handles click events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

## Test Utilities

### Backend Fixtures (`conftest.py`)
- `mock_redis_client`: Mocked Redis client
- `mock_mongodb_collection`: Mocked MongoDB collection
- `mock_pinecone_index`: Mocked Pinecone index
- `sample_user_profile`: Test user data
- `sample_memory_fragment`: Test memory data

### Frontend Utilities (`test-utils.tsx`)
- `render`: Custom render with providers
- `createMockUser`: User data generator
- `createMockChatMessage`: Message generator
- `waitForLoadingToFinish`: Async helper
- Accessibility testing helpers

## Best Practices

1. **Test Isolation**: Each test should be independent and not rely on other tests
2. **Mock External Services**: Always mock API calls, databases, and external services
3. **Test User Flows**: Include integration tests for complete user journeys
4. **Accessibility Testing**: Include a11y tests for all UI components
5. **Error Cases**: Test both success and failure scenarios
6. **Async Testing**: Use proper async/await patterns for asynchronous code

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Commits to main branch
- Scheduled daily runs

Failed tests will block merging and deployment.

## Coverage Goals

- **Unit Tests**: 80% coverage minimum
- **Integration Tests**: Cover all critical user paths
- **API Tests**: 100% endpoint coverage
- **Component Tests**: All interactive components
- **Accessibility**: WCAG AA compliance

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **Mock Failures**: Check that all external dependencies are properly mocked
3. **Async Timeouts**: Increase timeout for slow operations
4. **Flaky Tests**: Use proper wait utilities for async operations

### Debug Mode

```bash
# Backend
pytest -v -s tests/unit/test_memory_controller.py::TestMemoryController::test_assemble_context

# Frontend
npm run test -- --reporter=verbose ChatMessage.test.tsx
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Testing Library](https://testing-library.com/)
- [Jest Mock Functions](https://jestjs.io/docs/mock-functions)