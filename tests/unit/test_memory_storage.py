import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from src.memory.storage import MemoryStorage
from src.models.memory import UserProfile, MemoryFragment, InteractionLog


class TestMemoryStorage:
    """Test cases for MemoryStorage"""
    
    @pytest.fixture
    def mock_collection(self):
        """Create a mock MongoDB collection"""
        collection = MagicMock()
        # Setup async methods
        collection.insert_one = AsyncMock()
        collection.find_one = AsyncMock()
        collection.update_one = AsyncMock()
        collection.update_many = AsyncMock()
        collection.count_documents = AsyncMock()
        
        # Setup find cursor mock
        cursor = MagicMock()
        cursor.sort.return_value = cursor
        cursor.limit.return_value = cursor
        cursor.__aiter__ = AsyncMock(return_value=[])
        collection.find.return_value = cursor
        
        return collection
    
    @pytest.fixture
    def memory_storage(self, mock_collection):
        """Create a MemoryStorage instance with mocked MongoDB"""
        with patch('src.memory.storage.mongodb_manager') as mock_db:
            mock_db.get_collection.return_value = mock_collection
            storage = MemoryStorage()
            storage.db = mock_db
            return storage
    
    @pytest.mark.asyncio
    async def test_create_user_profile_success(self, memory_storage, mock_collection):
        """Test creating a user profile successfully"""
        # Setup
        user_profile = UserProfile(
            user_id="test_user",
            name="John Doe",
            age=75,
            conditions=["hypertension"],
            interests=["reading"]
        )
        mock_collection.insert_one.return_value.inserted_id = "507f1f77bcf86cd799439011"
        
        # Execute
        result = await memory_storage.create_user_profile(user_profile)
        
        # Assert
        assert result == "507f1f77bcf86cd799439011"
        mock_collection.insert_one.assert_called_once()
        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args["user_id"] == "test_user"
        assert call_args["name"] == "John Doe"
        assert call_args["age"] == 75
    
    @pytest.mark.asyncio
    async def test_create_user_profile_error(self, memory_storage, mock_collection):
        """Test error handling when creating user profile fails"""
        mock_collection.insert_one.side_effect = Exception("MongoDB error")
        
        user_profile = UserProfile(
            user_id="test_user",
            name="John Doe",
            age=75
        )
        
        with pytest.raises(Exception):
            await memory_storage.create_user_profile(user_profile)
    
    @pytest.mark.asyncio
    async def test_get_user_profile_exists(self, memory_storage, mock_collection):
        """Test retrieving an existing user profile"""
        # Setup mock data
        mock_data = {
            "_id": "507f1f77bcf86cd799439011",
            "user_id": "test_user",
            "name": "Jane Smith",
            "age": 80,
            "conditions": ["diabetes"],
            "interests": ["gardening"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        mock_collection.find_one.return_value = mock_data.copy()
        
        # Execute
        profile = await memory_storage.get_user_profile("test_user")
        
        # Assert
        assert profile is not None
        assert profile.user_id == "test_user"
        assert profile.name == "Jane Smith"
        assert profile.age == 80
        assert "diabetes" in profile.conditions
        mock_collection.find_one.assert_called_once_with({"user_id": "test_user"})
    
    @pytest.mark.asyncio
    async def test_get_user_profile_not_found(self, memory_storage, mock_collection):
        """Test retrieving a non-existent user profile"""
        mock_collection.find_one.return_value = None
        
        profile = await memory_storage.get_user_profile("unknown_user")
        
        assert profile is None
    
    @pytest.mark.asyncio
    async def test_get_user_profile_error(self, memory_storage, mock_collection):
        """Test error handling when retrieving user profile"""
        mock_collection.find_one.side_effect = Exception("MongoDB error")
        
        profile = await memory_storage.get_user_profile("test_user")
        
        assert profile is None
    
    @pytest.mark.asyncio
    async def test_update_user_profile_success(self, memory_storage, mock_collection):
        """Test updating a user profile successfully"""
        mock_collection.update_one.return_value.modified_count = 1
        
        updates = {"age": 81, "interests": ["gardening", "cooking"]}
        result = await memory_storage.update_user_profile("test_user", updates)
        
        assert result is True
        mock_collection.update_one.assert_called_once()
        call_args = mock_collection.update_one.call_args[0]
        assert call_args[0] == {"user_id": "test_user"}
        assert "updated_at" in call_args[1]["$set"]
        assert call_args[1]["$set"]["age"] == 81
    
    @pytest.mark.asyncio
    async def test_update_user_profile_not_found(self, memory_storage, mock_collection):
        """Test updating a non-existent user profile"""
        mock_collection.update_one.return_value.modified_count = 0
        
        result = await memory_storage.update_user_profile("unknown_user", {"age": 81})
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_store_memory_fragment_success(self, memory_storage, mock_collection):
        """Test storing a memory fragment successfully"""
        fragment = MemoryFragment(
            user_id="test_user",
            timestamp=datetime.utcnow(),
            type="health",
            content="User mentioned taking medication",
            tags=["medication", "health"],
            retention="active"
        )
        mock_collection.insert_one.return_value.inserted_id = "507f1f77bcf86cd799439012"
        
        result = await memory_storage.store_memory_fragment(fragment)
        
        assert result == "507f1f77bcf86cd799439012"
        mock_collection.insert_one.assert_called_once()
        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args["user_id"] == "test_user"
        assert call_args["type"] == "health"
        assert "medication" in call_args["tags"]
    
    @pytest.mark.asyncio
    async def test_get_active_memories(self, memory_storage, mock_collection):
        """Test retrieving active memories"""
        # Setup mock data
        mock_memories = [
            {
                "user_id": "test_user",
                "timestamp": datetime.utcnow(),
                "type": "health",
                "content": "Memory 1",
                "tags": ["health"],
                "retention": "active"
            },
            {
                "user_id": "test_user",
                "timestamp": datetime.utcnow() - timedelta(days=1),
                "type": "event",
                "content": "Memory 2",
                "tags": ["daily"],
                "retention": "active"
            }
        ]
        
        # Setup async iterator for cursor
        async def async_iter():
            for memory in mock_memories:
                yield memory.copy()
        
        cursor = mock_collection.find.return_value
        cursor.sort.return_value = cursor
        cursor.limit.return_value = cursor
        cursor.__aiter__.return_value = async_iter()
        
        # Execute
        memories = await memory_storage.get_active_memories("test_user", limit=10)
        
        # Assert
        assert len(memories) == 2
        assert memories[0].content == "Memory 1"
        assert memories[1].content == "Memory 2"
        
        mock_collection.find.assert_called_once_with({
            "user_id": "test_user",
            "retention": "active"
        })
        cursor.sort.assert_called_once_with("timestamp", -1)
        cursor.limit.assert_called_once_with(10)
    
    @pytest.mark.asyncio
    async def test_search_memories_by_tags(self, memory_storage, mock_collection):
        """Test searching memories by tags"""
        # Setup mock data
        mock_memories = [
            {
                "user_id": "test_user",
                "timestamp": datetime.utcnow(),
                "type": "health",
                "content": "Health memory",
                "tags": ["medication", "health"],
                "retention": "active"
            }
        ]
        
        async def async_iter():
            for memory in mock_memories:
                yield memory.copy()
        
        cursor = mock_collection.find.return_value
        cursor.sort.return_value = cursor
        cursor.__aiter__.return_value = async_iter()
        
        # Execute
        memories = await memory_storage.search_memories_by_tags(
            "test_user",
            ["medication", "appointment"],
            retention="active"
        )
        
        # Assert
        assert len(memories) == 1
        assert "medication" in memories[0].tags
        
        mock_collection.find.assert_called_once_with({
            "user_id": "test_user",
            "tags": {"$in": ["medication", "appointment"]},
            "retention": "active"
        })
    
    @pytest.mark.asyncio
    async def test_archive_old_memories(self, memory_storage, mock_collection):
        """Test archiving old memories"""
        mock_collection.update_many.return_value.modified_count = 5
        
        with patch('src.memory.storage.settings') as mock_settings:
            mock_settings.memory_active_days = 90
            count = await memory_storage.archive_old_memories()
        
        assert count == 5
        
        # Check the update query
        call_args = mock_collection.update_many.call_args[0]
        query = call_args[0]
        update = call_args[1]
        
        assert query["retention"] == "active"
        assert "$lt" in query["timestamp"]
        assert update["$set"]["retention"] == "archive"
    
    @pytest.mark.asyncio
    async def test_log_interaction(self, memory_storage, mock_collection):
        """Test logging an interaction"""
        log = InteractionLog(
            user_id="test_user",
            timestamp=datetime.utcnow(),
            user_message="Hello",
            ai_response="Hi there!",
            response_time_ms=150,
            context_size=1000,
            error=None
        )
        mock_collection.insert_one.return_value.inserted_id = "507f1f77bcf86cd799439013"
        
        result = await memory_storage.log_interaction(log)
        
        assert result == "507f1f77bcf86cd799439013"
        mock_collection.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_statistics(self, memory_storage, mock_collection):
        """Test getting user statistics"""
        # Setup mocks
        memory_storage.db.get_collection.side_effect = lambda name: {
            "memory_fragments": mock_collection,
            "interaction_logs": mock_collection
        }[name]
        
        mock_collection.count_documents.side_effect = [10, 5, 25]  # active, archive, interactions
        mock_collection.find_one.return_value = {
            "timestamp": datetime.utcnow()
        }
        
        # Execute
        stats = await memory_storage.get_user_statistics("test_user")
        
        # Assert
        assert stats["active_memories"] == 10
        assert stats["archived_memories"] == 5
        assert stats["total_interactions"] == 25
        assert stats["last_interaction"] is not None
        
        # Check count_documents calls
        assert mock_collection.count_documents.call_count == 3
        calls = mock_collection.count_documents.call_args_list
        assert calls[0][0][0] == {"user_id": "test_user", "retention": "active"}
        assert calls[1][0][0] == {"user_id": "test_user", "retention": "archive"}
        assert calls[2][0][0] == {"user_id": "test_user"}
    
    @pytest.mark.asyncio
    async def test_get_user_statistics_no_data(self, memory_storage, mock_collection):
        """Test getting statistics for user with no data"""
        memory_storage.db.get_collection.side_effect = lambda name: mock_collection
        
        mock_collection.count_documents.return_value = 0
        mock_collection.find_one.return_value = None
        
        stats = await memory_storage.get_user_statistics("new_user")
        
        assert stats["active_memories"] == 0
        assert stats["archived_memories"] == 0
        assert stats["total_interactions"] == 0
        assert stats["last_interaction"] is None