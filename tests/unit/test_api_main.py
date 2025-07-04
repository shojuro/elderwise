"""
Tests for main API endpoints and application lifecycle
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from src.api.main import app


class TestMainAPI:
    """Test cases for main API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        # Skip lifespan events for testing
        with TestClient(app) as client:
            yield client
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns correct information"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "ElderWise AI API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "operational"
    
    @patch('src.api.main.redis_manager')
    @patch('src.api.main.mongodb_manager')
    @patch('src.api.main.pinecone_manager')
    def test_health_check_all_services_healthy(self, mock_pinecone, mock_mongo, mock_redis, client):
        """Test health check when all services are healthy"""
        # Setup mocks
        mock_redis.get_client.return_value.ping.return_value = True
        mock_mongo.client.admin.command = AsyncMock(return_value=True)
        mock_pinecone.get_index.return_value.describe_index_stats.return_value = {}
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["services"]["redis"] == "connected"
        assert data["services"]["mongodb"] == "connected"
        assert data["services"]["pinecone"] == "connected"
    
    @patch('src.api.main.redis_manager')
    @patch('src.api.main.mongodb_manager')
    @patch('src.api.main.pinecone_manager')
    def test_health_check_redis_down(self, mock_pinecone, mock_mongo, mock_redis, client):
        """Test health check when Redis is down"""
        # Setup mocks
        mock_redis.get_client.return_value.ping.side_effect = Exception("Redis error")
        mock_mongo.client.admin.command = AsyncMock(return_value=True)
        mock_pinecone.get_index.return_value.describe_index_stats.return_value = {}
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["services"]["redis"] == "disconnected"
        assert data["services"]["mongodb"] == "connected"
        assert data["services"]["pinecone"] == "connected"
    
    @patch('src.api.main.redis_manager')
    @patch('src.api.main.mongodb_manager')
    @patch('src.api.main.pinecone_manager')
    def test_health_check_multiple_services_down(self, mock_pinecone, mock_mongo, mock_redis, client):
        """Test health check when multiple services are down"""
        # Setup mocks
        mock_redis.get_client.return_value.ping.side_effect = Exception("Redis error")
        mock_mongo.client.admin.command = AsyncMock(side_effect=Exception("MongoDB error"))
        mock_pinecone.get_index.return_value.describe_index_stats.side_effect = Exception("Pinecone error")
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["services"]["redis"] == "disconnected"
        assert data["services"]["mongodb"] == "disconnected"
        assert data["services"]["pinecone"] == "disconnected"
    
    def test_cors_headers(self, client):
        """Test CORS headers are properly set"""
        response = client.options("/", headers={"Origin": "http://localhost:3000"})
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers
    
    @patch('src.api.main.memory_scheduler')
    @patch('src.api.main.redis_manager')
    @patch('src.api.main.mongodb_manager')
    @patch('src.api.main.pinecone_manager')
    @pytest.mark.asyncio
    async def test_lifespan_startup(self, mock_pinecone, mock_mongo, mock_redis, mock_scheduler):
        """Test application startup lifecycle"""
        from src.api.main import lifespan
        
        # Setup mocks
        mock_redis.connect.return_value = None
        mock_mongo.connect = AsyncMock()
        mock_pinecone.connect.return_value = None
        mock_scheduler.start.return_value = None
        
        # Test startup
        app_mock = MagicMock()
        async with lifespan(app_mock):
            # Verify connections were established
            mock_redis.connect.assert_called_once()
            mock_mongo.connect.assert_called_once()
            mock_pinecone.connect.assert_called_once()
            mock_scheduler.start.assert_called_once()
    
    @patch('src.api.main.memory_scheduler')
    @patch('src.api.main.redis_manager')
    @patch('src.api.main.mongodb_manager')
    @patch('src.api.main.pinecone_manager')
    @pytest.mark.asyncio
    async def test_lifespan_shutdown(self, mock_pinecone, mock_mongo, mock_redis, mock_scheduler):
        """Test application shutdown lifecycle"""
        from src.api.main import lifespan
        
        # Setup mocks
        mock_redis.connect.return_value = None
        mock_redis.disconnect.return_value = None
        mock_mongo.connect = AsyncMock()
        mock_mongo.disconnect = AsyncMock()
        mock_pinecone.connect.return_value = None
        mock_scheduler.start.return_value = None
        mock_scheduler.stop.return_value = None
        
        # Test full lifecycle
        app_mock = MagicMock()
        async with lifespan(app_mock):
            pass
        
        # Verify cleanup was performed
        mock_scheduler.stop.assert_called_once()
        mock_redis.disconnect.assert_called_once()
        mock_mongo.disconnect.assert_called_once()
    
    @patch('src.api.main.redis_manager')
    @patch('src.api.main.mongodb_manager')
    @patch('src.api.main.pinecone_manager')
    @pytest.mark.asyncio
    async def test_lifespan_startup_failure(self, mock_pinecone, mock_mongo, mock_redis):
        """Test application startup failure handling"""
        from src.api.main import lifespan
        
        # Setup mock to fail
        mock_redis.connect.side_effect = Exception("Connection failed")
        
        # Test startup failure
        app_mock = MagicMock()
        with pytest.raises(Exception):
            async with lifespan(app_mock):
                pass