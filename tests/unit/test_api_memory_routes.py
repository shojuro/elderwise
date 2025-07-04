"""
Tests for memory management route endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from src.api.main import app
from src.models.memory import MemoryFragment


class TestMemoryRoutes:
    """Test cases for memory route endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        with TestClient(app) as client:
            yield client
    
    @pytest.fixture
    def mock_storage(self):
        """Mock memory storage"""
        with patch('src.api.routes.memory.storage') as mock:
            yield mock
    
    @pytest.fixture
    def mock_semantic(self):
        """Mock semantic memory"""
        with patch('src.api.routes.memory.semantic') as mock:
            yield mock
    
    @pytest.fixture
    def mock_session(self):
        """Mock session manager"""
        with patch('src.api.routes.memory.session') as mock:
            yield mock
    
    @pytest.fixture
    def sample_memory_fragment(self):
        """Sample memory fragment"""
        return MemoryFragment(
            user_id="test_user",
            timestamp=datetime.utcnow(),
            type="event",
            content="Doctor appointment at 2pm",
            tags=["appointment", "health"],
            retention="active"
        )
    
    @pytest.mark.asyncio
    async def test_create_memory_success(self, client, mock_storage, mock_semantic):
        """Test successful memory creation"""
        mock_storage.store_memory_fragment = AsyncMock(return_value="fragment_123")
        mock_semantic.store_memory_vector = AsyncMock(return_value="vector_456")
        
        request_data = {
            "user_id": "test_user",
            "content": "Important memory about medication",
            "type": "health",
            "tags": ["medication", "important"],
            "metadata": {"priority": "high"}
        }
        
        response = client.post("/memory/create", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Memory created successfully"
        assert data["fragment_id"] == "fragment_123"
        assert data["vector_id"] == "vector_456"
        
        # Verify storage calls
        mock_storage.store_memory_fragment.assert_called_once()
        fragment = mock_storage.store_memory_fragment.call_args[0][0]
        assert fragment.user_id == "test_user"
        assert fragment.content == "Important memory about medication"
        assert fragment.type == "health"
        assert "medication" in fragment.tags
        
        # Verify semantic storage
        mock_semantic.store_memory_vector.assert_called_once()
        sem_args = mock_semantic.store_memory_vector.call_args[1]
        assert sem_args["user_id"] == "test_user"
        assert sem_args["content"] == "Important memory about medication"
        assert sem_args["metadata"]["fragment_id"] == "fragment_123"
    
    @pytest.mark.asyncio
    async def test_create_memory_invalid_type(self, client):
        """Test memory creation with invalid type"""
        request_data = {
            "user_id": "test_user",
            "content": "Test content",
            "type": "invalid_type"  # Not in allowed pattern
        }
        
        response = client.post("/memory/create", json=request_data)
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_search_memories_success(self, client, mock_semantic):
        """Test successful memory search"""
        mock_semantic.search_memories = AsyncMock(return_value=[
            {
                "id": "vec1",
                "score": 0.95,
                "content": "Memory about medication",
                "timestamp": "2024-01-01T10:00:00",
                "tags": ["health", "medication"],
                "type": "health"
            },
            {
                "id": "vec2",
                "score": 0.87,
                "content": "Doctor appointment",
                "timestamp": "2024-01-02T14:00:00",
                "tags": ["appointment"],
                "type": "event"
            }
        ])
        
        request_data = {
            "user_id": "test_user",
            "query": "Tell me about my health",
            "top_k": 5,
            "retention": "active"
        }
        
        response = client.post("/memory/search", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "Tell me about my health"
        assert data["count"] == 2
        assert len(data["results"]) == 2
        assert data["results"][0]["score"] == 0.95
        
        # Verify semantic search was called
        mock_semantic.search_memories.assert_called_once_with(
            user_id="test_user",
            query="Tell me about my health",
            top_k=5,
            retention="active"
        )
    
    @pytest.mark.asyncio
    async def test_search_memories_no_results(self, client, mock_semantic):
        """Test memory search with no results"""
        mock_semantic.search_memories = AsyncMock(return_value=[])
        
        request_data = {
            "user_id": "test_user",
            "query": "Non-existent topic"
        }
        
        response = client.post("/memory/search", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []
    
    @pytest.mark.asyncio
    async def test_get_recent_memories_success(self, client, mock_storage, sample_memory_fragment):
        """Test retrieving recent memories"""
        mock_storage.get_active_memories = AsyncMock(return_value=[
            sample_memory_fragment,
            MemoryFragment(
                user_id="test_user",
                timestamp=datetime.utcnow(),
                type="preference",
                content="Likes Italian food",
                tags=["food", "preference"],
                retention="active"
            )
        ])
        
        response = client.get("/memory/test_user/recent?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test_user"
        assert data["count"] == 2
        assert len(data["memories"]) == 2
        assert data["memories"][0]["content"] == "Doctor appointment at 2pm"
        
        mock_storage.get_active_memories.assert_called_once_with("test_user", limit=10)
    
    @pytest.mark.asyncio
    async def test_get_recent_memories_with_limit(self, client, mock_storage):
        """Test retrieving recent memories with custom limit"""
        mock_storage.get_active_memories = AsyncMock(return_value=[])
        
        response = client.get("/memory/test_user/recent?limit=25")
        
        assert response.status_code == 200
        mock_storage.get_active_memories.assert_called_once_with("test_user", limit=25)
    
    @pytest.mark.asyncio
    async def test_get_recent_memories_invalid_limit(self, client):
        """Test retrieving recent memories with invalid limit"""
        response = client.get("/memory/test_user/recent?limit=100")  # Over max limit
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_session_history_success(self, client, mock_session):
        """Test retrieving session history"""
        mock_session.get_recent_interactions.return_value = [
            {
                "timestamp": "2024-01-01T10:00:00",
                "user": "Hello",
                "ai": "Hi there!"
            },
            {
                "timestamp": "2024-01-01T10:01:00",
                "user": "How are you?",
                "ai": "I'm doing well!"
            }
        ]
        
        response = client.get("/memory/test_user/session")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test_user"
        assert data["count"] == 2
        assert len(data["interactions"]) == 2
        assert data["interactions"][0]["user"] == "Hello"
        
        mock_session.get_recent_interactions.assert_called_once_with("test_user", limit=None)
    
    @pytest.mark.asyncio
    async def test_get_session_history_with_limit(self, client, mock_session):
        """Test retrieving session history with limit"""
        mock_session.get_recent_interactions.return_value = []
        
        response = client.get("/memory/test_user/session?limit=5")
        
        assert response.status_code == 200
        mock_session.get_recent_interactions.assert_called_once_with("test_user", limit=5)
    
    @pytest.mark.asyncio
    async def test_clear_session_success(self, client, mock_session):
        """Test clearing session history"""
        mock_session.clear_session.return_value = None
        
        response = client.delete("/memory/test_user/session")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Session cleared successfully"
        assert data["user_id"] == "test_user"
        
        mock_session.clear_session.assert_called_once_with("test_user")
    
    @pytest.mark.asyncio
    async def test_clear_session_error(self, client, mock_session):
        """Test error handling when clearing session fails"""
        mock_session.clear_session.side_effect = Exception("Redis error")
        
        response = client.delete("/memory/test_user/session")
        
        assert response.status_code == 500
        assert "Redis error" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_trigger_archive_success(self, client, mock_storage):
        """Test triggering memory archive process"""
        mock_storage.archive_old_memories = AsyncMock(return_value=15)
        
        response = client.post("/memory/archive")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Archive process completed"
        assert data["memories_archived"] == 15
        
        mock_storage.archive_old_memories.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_memory_tags_success(self, client, mock_storage):
        """Test retrieving unique memory tags"""
        memories = [
            MemoryFragment(
                user_id="test_user",
                timestamp=datetime.utcnow(),
                type="health",
                content="Content 1",
                tags=["health", "medication"],
                retention="active"
            ),
            MemoryFragment(
                user_id="test_user",
                timestamp=datetime.utcnow(),
                type="event",
                content="Content 2",
                tags=["appointment", "health"],
                retention="active"
            ),
            MemoryFragment(
                user_id="test_user",
                timestamp=datetime.utcnow(),
                type="preference",
                content="Content 3",
                tags=["food", "italian"],
                retention="active"
            )
        ]
        
        mock_storage.get_active_memories = AsyncMock(return_value=memories)
        
        response = client.get("/memory/test_user/tags")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test_user"
        assert data["count"] == 5  # Unique tags
        assert "appointment" in data["tags"]
        assert "food" in data["tags"]
        assert "health" in data["tags"]
        assert "italian" in data["tags"]
        assert "medication" in data["tags"]
        assert data["tags"] == sorted(data["tags"])  # Should be sorted
    
    @pytest.mark.asyncio
    async def test_get_memory_tags_no_memories(self, client, mock_storage):
        """Test retrieving tags when user has no memories"""
        mock_storage.get_active_memories = AsyncMock(return_value=[])
        
        response = client.get("/memory/test_user/tags")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["tags"] == []
    
    @pytest.mark.asyncio
    async def test_search_memories_validation(self, client):
        """Test search request validation"""
        # Invalid top_k
        response = client.post("/memory/search", json={
            "user_id": "test",
            "query": "test",
            "top_k": 50  # Over limit
        })
        assert response.status_code == 422
        
        # Invalid retention
        response = client.post("/memory/search", json={
            "user_id": "test",
            "query": "test",
            "retention": "invalid"
        })
        assert response.status_code == 422