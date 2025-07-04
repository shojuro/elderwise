"""
Tests for AI route endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import uuid
from datetime import datetime
from src.api.main import app
from src.ai.response import AIResponse


class TestAIRoutes:
    """Test cases for AI route endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        with TestClient(app) as client:
            yield client
    
    @pytest.fixture
    def mock_memory_controller(self):
        """Mock memory controller"""
        with patch('src.api.routes.ai.memory_controller') as mock:
            # Setup context assembly
            mock.assemble_context = AsyncMock(return_value={
                "context_string": "Test context",
                "user_profile": {"user_id": "test_user", "name": "Test User"},
                "recent_interactions": "Recent chat history",
                "relevant_memories": [{"content": "Memory 1", "score": 0.9}],
                "recent_fragments": []
            })
            
            # Setup interaction storage
            mock.store_interaction = AsyncMock()
            mock.storage.log_interaction = AsyncMock()
            
            yield mock
    
    @pytest.fixture
    def mock_ai_client(self):
        """Mock AI client"""
        with patch('src.api.routes.ai.ai_client') as mock:
            # Setup response generation
            mock.generate_response = AsyncMock(return_value=AIResponse(
                success=True,
                response="Hello! How can I help you today?",
                response_time_ms=150,
                tokens_used=50,
                provider="mistral",
                model="mistralai/Mistral-7B-Instruct-v0.3",
                error=None
            ))
            
            # Setup health check
            mock.health_check = AsyncMock(return_value={
                "overall_status": "healthy",
                "providers": {"mistral": "available"}
            })
            
            yield mock
    
    @pytest.mark.asyncio
    async def test_generate_response_success(self, client, mock_memory_controller, mock_ai_client):
        """Test successful response generation"""
        request_data = {
            "user_id": "test_user",
            "message": "Hello, how are you?",
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = client.post("/ai/respond", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Hello! How can I help you today?"
        assert data["response_time_ms"] == 150
        assert "session_id" in data
        assert data["context_summary"]["profile_loaded"] is True
        assert data["context_summary"]["relevant_memories_count"] == 1
        
        # Verify memory controller was called
        mock_memory_controller.assemble_context.assert_called_once_with(
            user_id="test_user",
            user_message="Hello, how are you?"
        )
        
        # Verify AI client was called
        mock_ai_client.generate_response.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_response_with_session_id(self, client, mock_memory_controller, mock_ai_client):
        """Test response generation with provided session ID"""
        session_id = str(uuid.uuid4())
        request_data = {
            "user_id": "test_user",
            "message": "Hello",
            "session_id": session_id
        }
        
        response = client.post("/ai/respond", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
    
    @pytest.mark.asyncio
    async def test_generate_response_ai_failure(self, client, mock_memory_controller, mock_ai_client):
        """Test handling of AI generation failure"""
        mock_ai_client.generate_response.return_value = AIResponse(
            success=False,
            response="",
            response_time_ms=0,
            tokens_used=0,
            provider="mistral",
            model="",
            error="Failed to generate response"
        )
        
        request_data = {
            "user_id": "test_user",
            "message": "Hello"
        }
        
        response = client.post("/ai/respond", json=request_data)
        
        assert response.status_code == 500
        assert "Failed to generate response" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_generate_response_memory_error(self, client, mock_memory_controller, mock_ai_client):
        """Test handling of memory assembly error"""
        mock_memory_controller.assemble_context.side_effect = Exception("Memory error")
        
        request_data = {
            "user_id": "test_user",
            "message": "Hello"
        }
        
        response = client.post("/ai/respond", json=request_data)
        
        assert response.status_code == 500
        assert "Memory error" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_generate_streaming_response(self, client, mock_memory_controller, mock_ai_client):
        """Test streaming response generation"""
        # Setup streaming mock
        async def mock_stream():
            yield "Hello "
            yield "there!"
        
        mock_ai_client.generate_streaming_response = mock_stream
        
        request_data = {
            "user_id": "test_user",
            "message": "Hello",
            "stream": True
        }
        
        response = client.post("/ai/respond/stream", json=request_data)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        
        # Check streaming content
        content = response.text
        assert "data: Hello " in content
        assert "data: there!" in content
        assert "data: [DONE]" in content
    
    @pytest.mark.asyncio
    async def test_validate_system_all_healthy(self, client, mock_memory_controller, mock_ai_client):
        """Test system validation when all components are healthy"""
        response = client.get("/ai/validate")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert data["components"]["ai_client"] is True
        assert data["components"]["memory_controller"] is True
        assert data["components"]["inference"] is True
        assert data["ai_health"]["overall_status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_validate_system_ai_unhealthy(self, client, mock_memory_controller, mock_ai_client):
        """Test system validation when AI client is unhealthy"""
        mock_ai_client.health_check.return_value = {
            "overall_status": "unhealthy",
            "providers": {}
        }
        
        response = client.get("/ai/validate")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["components"]["ai_client"] is False
        assert data["components"]["inference"] is False
    
    @pytest.mark.asyncio
    async def test_validate_system_memory_error(self, client, mock_memory_controller, mock_ai_client):
        """Test system validation when memory controller has error"""
        mock_memory_controller.assemble_context.side_effect = Exception("Memory error")
        
        response = client.get("/ai/validate")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["components"]["memory_controller"] is False
    
    def test_chat_request_validation(self, client):
        """Test request validation for chat endpoint"""
        # Missing required fields
        response = client.post("/ai/respond", json={})
        assert response.status_code == 422
        
        # Invalid temperature
        response = client.post("/ai/respond", json={
            "user_id": "test",
            "message": "Hello",
            "temperature": 2.0  # Out of range
        })
        assert response.status_code == 422
        
        # Invalid max_tokens
        response = client.post("/ai/respond", json={
            "user_id": "test",
            "message": "Hello",
            "max_tokens": 5000  # Out of range
        })
        assert response.status_code == 422
    
    @patch('src.api.routes.ai.BackgroundTasks')
    @pytest.mark.asyncio
    async def test_background_task_execution(self, mock_bg_tasks, client, mock_memory_controller, mock_ai_client):
        """Test that background tasks are properly scheduled"""
        mock_bg_instance = MagicMock()
        mock_bg_tasks.return_value = mock_bg_instance
        
        request_data = {
            "user_id": "test_user",
            "message": "Hello"
        }
        
        response = client.post("/ai/respond", json=request_data)
        
        assert response.status_code == 200
        
        # Verify background task was added
        mock_bg_instance.add_task.assert_called_once()
        call_args = mock_bg_instance.add_task.call_args[0]
        assert call_args[0].__name__ == "store_interaction_background"
        assert call_args[1] == "test_user"  # user_id
        assert call_args[3] == "Hello"  # user_message
    
    @pytest.mark.asyncio
    async def test_store_interaction_background(self, mock_memory_controller):
        """Test background interaction storage function"""
        from src.api.routes.ai import store_interaction_background
        
        await store_interaction_background(
            user_id="test_user",
            session_id="session_123",
            user_message="Test message",
            ai_response="Test response",
            context_used={"test": "context"},
            response_time_ms=100
        )
        
        # Verify memory controller methods were called
        mock_memory_controller.store_interaction.assert_called_once_with(
            user_id="test_user",
            user_message="Test message",
            ai_response="Test response",
            context_used={"test": "context"},
            response_time_ms=100
        )
        
        mock_memory_controller.storage.log_interaction.assert_called_once()
        log_call = mock_memory_controller.storage.log_interaction.call_args[0][0]
        assert log_call.user_id == "test_user"
        assert log_call.session_id == "session_123"
        assert log_call.user_message == "Test message"
        assert log_call.ai_response == "Test response"