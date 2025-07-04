"""
Integration tests for API endpoints working together
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import uuid
from src.api.main import app
from src.models.memory import UserProfile, MemoryFragment
from src.ai.response import AIResponse


class TestAPIIntegration:
    """Integration tests for API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        with TestClient(app) as client:
            yield client
    
    @pytest.fixture
    def mock_all_services(self):
        """Mock all external services"""
        with patch('src.api.routes.users.storage') as mock_storage, \
             patch('src.api.routes.memory.storage', mock_storage), \
             patch('src.api.routes.memory.semantic') as mock_semantic, \
             patch('src.api.routes.memory.session') as mock_session, \
             patch('src.api.routes.ai.memory_controller') as mock_controller, \
             patch('src.api.routes.ai.ai_client') as mock_ai:
            
            yield {
                'storage': mock_storage,
                'semantic': mock_semantic,
                'session': mock_session,
                'controller': mock_controller,
                'ai_client': mock_ai
            }
    
    @pytest.mark.asyncio
    async def test_complete_user_flow(self, client, mock_all_services):
        """Test complete user flow: create user -> add memories -> chat -> get stats"""
        storage = mock_all_services['storage']
        semantic = mock_all_services['semantic']
        controller = mock_all_services['controller']
        ai_client = mock_all_services['ai_client']
        
        # Step 1: Create a new user
        storage.get_user_profile = AsyncMock(side_effect=[None, UserProfile(
            user_id="new_user",
            name="Alice Johnson",
            age=72,
            conditions=["arthritis"],
            interests=["painting"]
        )])
        storage.create_user_profile = AsyncMock(return_value="profile_123")
        
        create_response = client.post("/users/create", json={
            "user_id": "new_user",
            "name": "Alice Johnson",
            "age": 72,
            "conditions": ["arthritis"],
            "interests": ["painting"]
        })
        
        assert create_response.status_code == 200
        assert create_response.json()["user_id"] == "new_user"
        
        # Step 2: Add a memory for the user
        storage.store_memory_fragment = AsyncMock(return_value="fragment_456")
        semantic.store_memory_vector = AsyncMock(return_value="vector_789")
        
        memory_response = client.post("/memory/create", json={
            "user_id": "new_user",
            "content": "Alice loves watercolor painting, especially landscapes",
            "type": "preference",
            "tags": ["painting", "hobby", "watercolor"]
        })
        
        assert memory_response.status_code == 200
        assert memory_response.json()["fragment_id"] == "fragment_456"
        
        # Step 3: Have a conversation
        controller.assemble_context = AsyncMock(return_value={
            "context_string": "User: Alice, 72, arthritis, loves painting",
            "user_profile": {"user_id": "new_user", "name": "Alice Johnson"},
            "recent_interactions": "",
            "relevant_memories": [{"content": "Loves watercolor painting", "score": 0.95}],
            "recent_fragments": []
        })
        
        ai_client.generate_response = AsyncMock(return_value=AIResponse(
            success=True,
            response="I remember you enjoy watercolor painting! How has your art been going?",
            response_time_ms=200,
            tokens_used=50,
            provider="mistral",
            model="mistralai/Mistral-7B-Instruct-v0.3"
        ))
        
        controller.store_interaction = AsyncMock()
        controller.storage.log_interaction = AsyncMock()
        
        chat_response = client.post("/ai/respond", json={
            "user_id": "new_user",
            "message": "What do you remember about my hobbies?"
        })
        
        assert chat_response.status_code == 200
        assert "watercolor painting" in chat_response.json()["response"]
        
        # Step 4: Get user statistics
        storage.get_user_statistics = AsyncMock(return_value={
            "active_memories": 1,
            "archived_memories": 0,
            "total_interactions": 1,
            "last_interaction": datetime.utcnow().isoformat()
        })
        
        stats_response = client.get("/users/new_user/stats")
        
        assert stats_response.status_code == 200
        stats_data = stats_response.json()
        assert stats_data["statistics"]["active_memories"] == 1
        assert stats_data["statistics"]["total_interactions"] == 1
    
    @pytest.mark.asyncio
    async def test_memory_search_and_chat_integration(self, client, mock_all_services):
        """Test memory search integration with chat context"""
        semantic = mock_all_services['semantic']
        controller = mock_all_services['controller']
        ai_client = mock_all_services['ai_client']
        
        # Setup semantic search to return health-related memories
        semantic.search_memories = AsyncMock(return_value=[
            {
                "id": "vec1",
                "score": 0.92,
                "content": "Takes blood pressure medication daily",
                "type": "health",
                "tags": ["medication", "health"]
            },
            {
                "id": "vec2",
                "score": 0.85,
                "content": "Doctor appointment last Tuesday",
                "type": "event",
                "tags": ["appointment", "health"]
            }
        ])
        
        # Search for health memories
        search_response = client.post("/memory/search", json={
            "user_id": "test_user",
            "query": "health and medications",
            "top_k": 5
        })
        
        assert search_response.status_code == 200
        search_data = search_response.json()
        assert search_data["count"] == 2
        assert "blood pressure medication" in search_data["results"][0]["content"]
        
        # Now use this in a chat context
        controller.assemble_context = AsyncMock(return_value={
            "context_string": "User has health concerns. Takes blood pressure medication.",
            "user_profile": {"user_id": "test_user", "name": "Test User"},
            "recent_interactions": "",
            "relevant_memories": search_data["results"],
            "recent_fragments": []
        })
        
        ai_client.generate_response = AsyncMock(return_value=AIResponse(
            success=True,
            response="I see you take blood pressure medication daily. It's important to maintain your schedule.",
            response_time_ms=180,
            tokens_used=40,
            provider="mistral",
            model="mistralai/Mistral-7B-Instruct-v0.3"
        ))
        
        controller.store_interaction = AsyncMock()
        controller.storage.log_interaction = AsyncMock()
        
        chat_response = client.post("/ai/respond", json={
            "user_id": "test_user",
            "message": "Do I have any medications to take?"
        })
        
        assert chat_response.status_code == 200
        assert "blood pressure medication" in chat_response.json()["response"]
        assert chat_response.json()["context_summary"]["relevant_memories_count"] == 2
    
    @pytest.mark.asyncio
    async def test_session_management_flow(self, client, mock_all_services):
        """Test session management across multiple interactions"""
        session = mock_all_services['session']
        controller = mock_all_services['controller']
        ai_client = mock_all_services['ai_client']
        
        session_id = str(uuid.uuid4())
        
        # First interaction
        session.get_recent_interactions.return_value = []
        controller.assemble_context = AsyncMock(return_value={
            "context_string": "First interaction",
            "user_profile": {"user_id": "test_user"},
            "recent_interactions": "",
            "relevant_memories": [],
            "recent_fragments": []
        })
        
        ai_client.generate_response = AsyncMock(return_value=AIResponse(
            success=True,
            response="Hello! How can I help you today?",
            response_time_ms=100,
            tokens_used=20,
            provider="mistral",
            model="mistralai/Mistral-7B-Instruct-v0.3"
        ))
        
        controller.store_interaction = AsyncMock()
        controller.storage.log_interaction = AsyncMock()
        
        first_response = client.post("/ai/respond", json={
            "user_id": "test_user",
            "message": "Hello",
            "session_id": session_id
        })
        
        assert first_response.status_code == 200
        assert first_response.json()["session_id"] == session_id
        
        # Check session history
        session.get_recent_interactions.return_value = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "user": "Hello",
                "ai": "Hello! How can I help you today?"
            }
        ]
        
        history_response = client.get(f"/memory/test_user/session")
        
        assert history_response.status_code == 200
        assert history_response.json()["count"] == 1
        assert history_response.json()["interactions"][0]["user"] == "Hello"
        
        # Clear session
        session.clear_session.return_value = None
        clear_response = client.delete(f"/memory/test_user/session")
        
        assert clear_response.status_code == 200
        session.clear_session.assert_called_once_with("test_user")
    
    @pytest.mark.asyncio
    async def test_memory_lifecycle(self, client, mock_all_services):
        """Test memory creation, retrieval, and archival"""
        storage = mock_all_services['storage']
        semantic = mock_all_services['semantic']
        
        # Create multiple memories
        storage.store_memory_fragment = AsyncMock(side_effect=["frag1", "frag2", "frag3"])
        semantic.store_memory_vector = AsyncMock(side_effect=["vec1", "vec2", "vec3"])
        
        memory_types = [
            ("health", ["medication", "daily"]),
            ("event", ["appointment", "doctor"]),
            ("preference", ["food", "italian"])
        ]
        
        for mem_type, tags in memory_types:
            response = client.post("/memory/create", json={
                "user_id": "test_user",
                "content": f"Memory of type {mem_type}",
                "type": mem_type,
                "tags": tags
            })
            assert response.status_code == 200
        
        # Get recent memories
        storage.get_active_memories = AsyncMock(return_value=[
            MemoryFragment(
                user_id="test_user",
                timestamp=datetime.utcnow(),
                type=mem_type,
                content=f"Memory of type {mem_type}",
                tags=tags,
                retention="active"
            )
            for mem_type, tags in memory_types
        ])
        
        recent_response = client.get("/memory/test_user/recent?limit=10")
        
        assert recent_response.status_code == 200
        assert recent_response.json()["count"] == 3
        
        # Get all tags
        tags_response = client.get("/memory/test_user/tags")
        
        assert tags_response.status_code == 200
        all_tags = tags_response.json()["tags"]
        assert "medication" in all_tags
        assert "appointment" in all_tags
        assert "italian" in all_tags
        
        # Archive old memories
        storage.archive_old_memories = AsyncMock(return_value=2)
        archive_response = client.post("/memory/archive")
        
        assert archive_response.status_code == 200
        assert archive_response.json()["memories_archived"] == 2
    
    @pytest.mark.asyncio
    async def test_error_propagation(self, client, mock_all_services):
        """Test that errors are properly propagated through the API"""
        storage = mock_all_services['storage']
        controller = mock_all_services['controller']
        
        # User not found error
        storage.get_user_profile = AsyncMock(return_value=None)
        response = client.get("/users/nonexistent_user")
        assert response.status_code == 404
        
        # Memory assembly error
        controller.assemble_context = AsyncMock(side_effect=Exception("Database connection lost"))
        response = client.post("/ai/respond", json={
            "user_id": "test_user",
            "message": "Hello"
        })
        assert response.status_code == 500
        assert "Database connection lost" in response.json()["detail"]
        
        # Storage error during memory creation
        storage.store_memory_fragment = AsyncMock(side_effect=Exception("Storage full"))
        response = client.post("/memory/create", json={
            "user_id": "test_user",
            "content": "Test",
            "type": "event"
        })
        assert response.status_code == 500
        assert "Storage full" in response.json()["detail"]