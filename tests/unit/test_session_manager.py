import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime
from src.memory.session import SessionManager


class TestSessionManager:
    """Test cases for SessionManager"""
    
    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis client"""
        mock = MagicMock()
        return mock
    
    @pytest.fixture
    def session_manager(self, mock_redis):
        """Create a SessionManager instance with mocked Redis"""
        with patch('src.memory.session.redis_manager') as mock_redis_manager:
            mock_redis_manager.get_client.return_value = mock_redis
            manager = SessionManager()
            return manager
    
    def test_get_session_key(self, session_manager):
        """Test session key generation"""
        key = session_manager._get_session_key("user123")
        assert key == "session:user123:history"
    
    def test_add_interaction_success(self, session_manager, mock_redis):
        """Test adding an interaction successfully"""
        # Execute
        session_manager.add_interaction(
            user_id="user123",
            user_message="Hello",
            ai_response="Hi there!"
        )
        
        # Assert Redis operations
        assert mock_redis.rpush.called
        assert mock_redis.ltrim.called
        assert mock_redis.expire.called
        
        # Check the interaction data
        call_args = mock_redis.rpush.call_args[0]
        assert call_args[0] == "session:user123:history"
        
        interaction_data = json.loads(call_args[1])
        assert interaction_data["user"] == "Hello"
        assert interaction_data["ai"] == "Hi there!"
        assert "timestamp" in interaction_data
        
        # Check TTL was set
        expire_call = mock_redis.expire.call_args[0]
        assert expire_call[0] == "session:user123:history"
        assert expire_call[1] == 86400  # 24 hours
    
    def test_add_interaction_error(self, session_manager, mock_redis):
        """Test error handling when adding interaction fails"""
        mock_redis.rpush.side_effect = Exception("Redis error")
        
        with pytest.raises(Exception):
            session_manager.add_interaction(
                user_id="user123",
                user_message="Hello",
                ai_response="Hi"
            )
    
    def test_get_recent_interactions_with_data(self, session_manager, mock_redis):
        """Test retrieving recent interactions"""
        # Setup mock data
        interaction1 = json.dumps({
            "timestamp": "2024-01-01T10:00:00",
            "user": "Hello",
            "ai": "Hi there!"
        })
        interaction2 = json.dumps({
            "timestamp": "2024-01-01T10:01:00",
            "user": "How are you?",
            "ai": "I'm doing well!"
        })
        
        mock_redis.lrange.return_value = [interaction1, interaction2]
        
        # Execute
        interactions = session_manager.get_recent_interactions("user123")
        
        # Assert
        assert len(interactions) == 2
        assert interactions[0]["user"] == "Hello"
        assert interactions[1]["user"] == "How are you?"
        
        # Check Redis call
        mock_redis.lrange.assert_called_once()
        call_args = mock_redis.lrange.call_args[0]
        assert call_args[0] == "session:user123:history"
    
    def test_get_recent_interactions_with_limit(self, session_manager, mock_redis):
        """Test retrieving interactions with custom limit"""
        mock_redis.lrange.return_value = []
        
        # Execute with custom limit
        session_manager.get_recent_interactions("user123", limit=5)
        
        # Check Redis was called with correct limit
        call_args = mock_redis.lrange.call_args[0]
        assert call_args[1] == -5
        assert call_args[2] == -1
    
    def test_get_recent_interactions_invalid_json(self, session_manager, mock_redis):
        """Test handling of invalid JSON in interactions"""
        # Setup with one valid and one invalid interaction
        valid_interaction = json.dumps({"user": "Hello", "ai": "Hi"})
        invalid_interaction = "invalid json {"
        
        mock_redis.lrange.return_value = [valid_interaction, invalid_interaction]
        
        # Execute
        interactions = session_manager.get_recent_interactions("user123")
        
        # Should only return the valid interaction
        assert len(interactions) == 1
        assert interactions[0]["user"] == "Hello"
    
    def test_get_recent_interactions_error(self, session_manager, mock_redis):
        """Test error handling when retrieving interactions"""
        mock_redis.lrange.side_effect = Exception("Redis error")
        
        # Should return empty list on error
        interactions = session_manager.get_recent_interactions("user123")
        assert interactions == []
    
    def test_clear_session_success(self, session_manager, mock_redis):
        """Test clearing session successfully"""
        session_manager.clear_session("user123")
        
        mock_redis.delete.assert_called_once_with("session:user123:history")
    
    def test_clear_session_error(self, session_manager, mock_redis):
        """Test error handling when clearing session"""
        mock_redis.delete.side_effect = Exception("Redis error")
        
        with pytest.raises(Exception):
            session_manager.clear_session("user123")
    
    def test_format_recent_context_with_interactions(self, session_manager, mock_redis):
        """Test formatting context with interactions"""
        # Setup mock interactions
        interactions = [
            {
                "timestamp": "2024-01-01T10:00:00",
                "user": "Hello",
                "ai": "Hi there!"
            },
            {
                "timestamp": "2024-01-01T10:01:00",
                "user": "How are you?",
                "ai": "I'm doing well, thank you!"
            }
        ]
        
        # Mock get_recent_interactions
        with patch.object(session_manager, 'get_recent_interactions', return_value=interactions):
            context = session_manager.format_recent_context("user123")
        
        # Assert formatting
        assert "[2024-01-01T10:00:00]" in context
        assert "User: Hello" in context
        assert "AI: Hi there!" in context
        assert "[2024-01-01T10:01:00]" in context
        assert "User: How are you?" in context
        assert "AI: I'm doing well, thank you!" in context
    
    def test_format_recent_context_no_interactions(self, session_manager, mock_redis):
        """Test formatting context with no interactions"""
        with patch.object(session_manager, 'get_recent_interactions', return_value=[]):
            context = session_manager.format_recent_context("user123")
        
        assert context == "No recent interactions."
    
    def test_format_recent_context_missing_fields(self, session_manager, mock_redis):
        """Test formatting context with missing fields in interactions"""
        # Interaction with missing fields
        interactions = [
            {
                "user": "Hello",  # Missing timestamp and ai
            },
            {
                "timestamp": "2024-01-01T10:00:00",
                "ai": "Response"  # Missing user
            }
        ]
        
        with patch.object(session_manager, 'get_recent_interactions', return_value=interactions):
            context = session_manager.format_recent_context("user123")
        
        # Should handle missing fields gracefully
        assert "User: Hello" in context
        assert "AI: Response" in context
        assert "[]" in context  # Empty timestamp for first interaction
    
    @patch('src.memory.session.settings')
    def test_memory_context_limit(self, mock_settings, session_manager, mock_redis):
        """Test that memory context limit is respected"""
        mock_settings.memory_context_limit = 5
        
        session_manager.add_interaction("user123", "Message", "Response")
        
        # Check ltrim was called with correct limit
        ltrim_call = mock_redis.ltrim.call_args[0]
        assert ltrim_call[1] == -5
        assert ltrim_call[2] == -1