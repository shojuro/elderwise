"""
Tests for user management route endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from src.api.main import app
from src.models.memory import UserProfile


class TestUserRoutes:
    """Test cases for user route endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        with TestClient(app) as client:
            yield client
    
    @pytest.fixture
    def mock_storage(self):
        """Mock memory storage"""
        with patch('src.api.routes.users.storage') as mock:
            yield mock
    
    @pytest.fixture
    def sample_user(self):
        """Sample user profile"""
        return UserProfile(
            user_id="test_user_123",
            name="John Doe",
            age=75,
            conditions=["hypertension", "diabetes"],
            interests=["gardening", "reading"]
        )
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, client, mock_storage):
        """Test successful user creation"""
        mock_storage.get_user_profile = AsyncMock(return_value=None)
        mock_storage.create_user_profile = AsyncMock(return_value="profile_123")
        
        request_data = {
            "user_id": "new_user",
            "name": "Jane Smith",
            "age": 80,
            "conditions": ["arthritis"],
            "interests": ["cooking", "music"]
        }
        
        response = client.post("/users/create", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User profile created successfully"
        assert data["user_id"] == "new_user"
        assert data["profile_id"] == "profile_123"
        
        # Verify storage calls
        mock_storage.get_user_profile.assert_called_once_with("new_user")
        mock_storage.create_user_profile.assert_called_once()
        created_profile = mock_storage.create_user_profile.call_args[0][0]
        assert created_profile.user_id == "new_user"
        assert created_profile.name == "Jane Smith"
        assert created_profile.age == 80
    
    @pytest.mark.asyncio
    async def test_create_user_already_exists(self, client, mock_storage, sample_user):
        """Test user creation when user already exists"""
        mock_storage.get_user_profile = AsyncMock(return_value=sample_user)
        
        request_data = {
            "user_id": "test_user_123",
            "name": "John Doe",
            "age": 75
        }
        
        response = client.post("/users/create", json=request_data)
        
        assert response.status_code == 409
        assert "User already exists" in response.json()["detail"]
        
        # Verify create was not called
        mock_storage.create_user_profile.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_user_validation_error(self, client):
        """Test user creation with invalid data"""
        # Age out of range
        response = client.post("/users/create", json={
            "user_id": "test",
            "name": "Test",
            "age": 200  # Invalid age
        })
        assert response.status_code == 422
        
        # Missing required fields
        response = client.post("/users/create", json={
            "user_id": "test"
        })
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_user_success(self, client, mock_storage, sample_user):
        """Test successful user retrieval"""
        mock_storage.get_user_profile = AsyncMock(return_value=sample_user)
        
        response = client.get("/users/test_user_123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test_user_123"
        assert data["name"] == "John Doe"
        assert data["age"] == 75
        assert "hypertension" in data["conditions"]
        
        mock_storage.get_user_profile.assert_called_once_with("test_user_123")
    
    @pytest.mark.asyncio
    async def test_get_user_not_found(self, client, mock_storage):
        """Test user retrieval when user doesn't exist"""
        mock_storage.get_user_profile = AsyncMock(return_value=None)
        
        response = client.get("/users/unknown_user")
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_update_user_success(self, client, mock_storage, sample_user):
        """Test successful user update"""
        mock_storage.get_user_profile = AsyncMock(side_effect=[sample_user, sample_user])
        mock_storage.update_user_profile = AsyncMock(return_value=True)
        
        update_data = {
            "age": 76,
            "interests": ["gardening", "reading", "painting"]
        }
        
        response = client.put("/users/test_user_123", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User profile updated successfully"
        assert "profile" in data
        
        # Verify update was called with correct data
        mock_storage.update_user_profile.assert_called_once()
        call_args = mock_storage.update_user_profile.call_args[0]
        assert call_args[0] == "test_user_123"
        assert call_args[1]["age"] == 76
        assert "interests" in call_args[1]
    
    @pytest.mark.asyncio
    async def test_update_user_not_found(self, client, mock_storage):
        """Test user update when user doesn't exist"""
        mock_storage.get_user_profile = AsyncMock(return_value=None)
        
        response = client.put("/users/unknown_user", json={"age": 80})
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_update_user_no_updates(self, client, mock_storage, sample_user):
        """Test user update with no data provided"""
        mock_storage.get_user_profile = AsyncMock(return_value=sample_user)
        
        response = client.put("/users/test_user_123", json={})
        
        assert response.status_code == 400
        assert "No updates provided" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_update_user_failed(self, client, mock_storage, sample_user):
        """Test user update when storage fails"""
        mock_storage.get_user_profile = AsyncMock(return_value=sample_user)
        mock_storage.update_user_profile = AsyncMock(return_value=False)
        
        response = client.put("/users/test_user_123", json={"age": 76})
        
        assert response.status_code == 500
        assert "Failed to update user profile" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_user_stats_success(self, client, mock_storage, sample_user):
        """Test successful user statistics retrieval"""
        mock_storage.get_user_profile = AsyncMock(return_value=sample_user)
        mock_storage.get_user_statistics = AsyncMock(return_value={
            "active_memories": 50,
            "archived_memories": 150,
            "total_interactions": 200,
            "last_interaction": "2024-01-01T10:00:00"
        })
        
        response = client.get("/users/test_user_123/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test_user_123"
        assert data["name"] == "John Doe"
        assert data["statistics"]["active_memories"] == 50
        assert data["statistics"]["total_interactions"] == 200
        
        mock_storage.get_user_statistics.assert_called_once_with("test_user_123")
    
    @pytest.mark.asyncio
    async def test_get_user_stats_not_found(self, client, mock_storage):
        """Test user statistics when user doesn't exist"""
        mock_storage.get_user_profile = AsyncMock(return_value=None)
        
        response = client.get("/users/unknown_user/stats")
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_create_user_storage_error(self, client, mock_storage):
        """Test error handling when storage fails during creation"""
        mock_storage.get_user_profile = AsyncMock(return_value=None)
        mock_storage.create_user_profile = AsyncMock(side_effect=Exception("Database error"))
        
        request_data = {
            "user_id": "new_user",
            "name": "Jane Smith",
            "age": 80
        }
        
        response = client.post("/users/create", json=request_data)
        
        assert response.status_code == 500
        assert "Database error" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_user_profile_defaults(self, client, mock_storage):
        """Test user creation with default values"""
        mock_storage.get_user_profile = AsyncMock(return_value=None)
        mock_storage.create_user_profile = AsyncMock(return_value="profile_123")
        
        request_data = {
            "user_id": "minimal_user",
            "name": "Minimal User",
            "age": 70
            # conditions and interests should default to empty lists
        }
        
        response = client.post("/users/create", json=request_data)
        
        assert response.status_code == 200
        
        # Check the created profile
        created_profile = mock_storage.create_user_profile.call_args[0][0]
        assert created_profile.conditions == []
        assert created_profile.interests == []