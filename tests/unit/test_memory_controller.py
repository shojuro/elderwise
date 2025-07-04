import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from src.memory.controller import MemoryController
from src.models.memory import MemoryFragment, UserProfile


class TestMemoryController:
    """Test cases for MemoryController"""
    
    @pytest.fixture
    def memory_controller(self):
        """Create a MemoryController instance with mocked dependencies"""
        with patch('src.memory.controller.SessionManager') as mock_session, \
             patch('src.memory.controller.MemoryStorage') as mock_storage, \
             patch('src.memory.controller.SemanticMemory') as mock_semantic:
            
            controller = MemoryController()
            # Return controller with access to mocked dependencies
            controller.session = mock_session.return_value
            controller.storage = mock_storage.return_value
            controller.semantic = mock_semantic.return_value
            
            return controller
    
    @pytest.mark.asyncio
    async def test_assemble_context_with_full_profile(self, memory_controller):
        """Test assembling context with a complete user profile"""
        # Setup mocks
        user_profile = UserProfile(
            user_id="test_user",
            name="John Doe",
            age=75,
            conditions=["hypertension", "diabetes"],
            interests=["gardening", "reading"]
        )
        
        memory_controller.storage.get_user_profile = AsyncMock(return_value=user_profile)
        memory_controller.session.format_recent_context = Mock(
            return_value="User: How are you?\nAI: I'm doing well, thank you!"
        )
        memory_controller.semantic.search_memories = AsyncMock(
            return_value=[
                {"content": "Discussed garden flowers", "score": 0.95},
                {"content": "Mentioned enjoying mystery novels", "score": 0.87}
            ]
        )
        memory_controller.storage.get_active_memories = AsyncMock(
            return_value=[
                MemoryFragment(
                    user_id="test_user",
                    timestamp=datetime.utcnow(),
                    type="health",
                    content="User mentioned taking medications",
                    tags=["medication"],
                    retention="active"
                )
            ]
        )
        
        # Execute
        context = await memory_controller.assemble_context("test_user", "Tell me about gardening")
        
        # Assert
        assert context["user_profile"]["name"] == "John Doe"
        assert context["user_profile"]["age"] == 75
        assert len(context["user_profile"]["conditions"]) == 2
        assert "How are you?" in context["recent_interactions"]
        assert len(context["relevant_memories"]) == 2
        assert context["relevant_memories"][0]["score"] == 0.95
        assert len(context["recent_fragments"]) == 1
        assert "Tell me about gardening" in context["context_string"]
        assert "John Doe" in context["context_string"]
        assert "hypertension" in context["context_string"]
    
    @pytest.mark.asyncio
    async def test_assemble_context_no_profile(self, memory_controller):
        """Test assembling context when user has no profile"""
        # Setup mocks
        memory_controller.storage.get_user_profile = AsyncMock(return_value=None)
        memory_controller.session.format_recent_context = Mock(return_value="")
        memory_controller.semantic.search_memories = AsyncMock(return_value=[])
        memory_controller.storage.get_active_memories = AsyncMock(return_value=[])
        
        # Execute
        context = await memory_controller.assemble_context("new_user", "Hello")
        
        # Assert
        assert context["user_profile"]["user_id"] == "new_user"
        assert context["user_profile"]["name"] == "Friend"
        assert context["user_profile"]["age"] == 0
        assert context["recent_interactions"] == ""
        assert len(context["relevant_memories"]) == 0
        assert "This is our first conversation" in context["context_string"]
    
    @pytest.mark.asyncio
    async def test_assemble_context_error_handling(self, memory_controller):
        """Test error handling in context assembly"""
        # Setup mock to raise exception
        memory_controller.storage.get_user_profile = AsyncMock(
            side_effect=Exception("Database error")
        )
        
        # Execute
        context = await memory_controller.assemble_context("test_user", "Hello")
        
        # Assert - should return minimal context
        assert context["user_profile"]["user_id"] == "test_user"
        assert context["user_profile"]["name"] == "Friend"
        assert context["context_string"] == "User says: Hello"
        assert len(context["relevant_memories"]) == 0
    
    @pytest.mark.asyncio
    async def test_store_interaction_significant(self, memory_controller):
        """Test storing a significant interaction"""
        # Setup mocks
        memory_controller.session.add_interaction = Mock()
        memory_controller.storage.store_memory_fragment = AsyncMock(return_value="fragment_123")
        memory_controller.semantic.store_memory_vector = AsyncMock(return_value="vector_456")
        
        # Execute with health-related message
        await memory_controller.store_interaction(
            user_id="test_user",
            user_message="I took my medication this morning",
            ai_response="That's great! It's important to stay consistent with your medications.",
            context_used={},
            response_time_ms=150
        )
        
        # Assert
        memory_controller.session.add_interaction.assert_called_once()
        memory_controller.storage.store_memory_fragment.assert_called_once()
        memory_controller.semantic.store_memory_vector.assert_called_once()
        
        # Check the fragment that was created
        fragment_call = memory_controller.storage.store_memory_fragment.call_args[0][0]
        assert fragment_call.type == "health"
        assert "medication" in fragment_call.tags
        assert fragment_call.retention == "active"
    
    @pytest.mark.asyncio
    async def test_store_interaction_not_significant(self, memory_controller):
        """Test storing a non-significant interaction"""
        # Setup mocks
        memory_controller.session.add_interaction = Mock()
        memory_controller.storage.store_memory_fragment = AsyncMock()
        memory_controller.semantic.store_memory_vector = AsyncMock()
        
        # Execute with brief message
        await memory_controller.store_interaction(
            user_id="test_user",
            user_message="Hi",
            ai_response="Hello!",
            context_used={},
            response_time_ms=50
        )
        
        # Assert - only session should be updated
        memory_controller.session.add_interaction.assert_called_once()
        memory_controller.storage.store_memory_fragment.assert_not_called()
        memory_controller.semantic.store_memory_vector.assert_not_called()
    
    def test_is_significant_interaction_keywords(self, memory_controller):
        """Test significance detection based on keywords"""
        # Health keyword
        assert memory_controller._is_significant_interaction(
            "I need to take my medication",
            "Remember to take it with food"
        )
        
        # Emotion keyword
        assert memory_controller._is_significant_interaction(
            "I feel lonely today",
            "I'm here to talk"
        )
        
        # No keywords, short
        assert not memory_controller._is_significant_interaction(
            "Hi",
            "Hello"
        )
    
    def test_is_significant_interaction_length(self, memory_controller):
        """Test significance detection based on message length"""
        # Long user message
        long_message = " ".join(["word"] * 15)
        assert memory_controller._is_significant_interaction(
            long_message,
            "Short response"
        )
        
        # Long AI response
        long_response = " ".join(["word"] * 25)
        assert memory_controller._is_significant_interaction(
            "Short message",
            long_response
        )
    
    def test_classify_interaction_type(self, memory_controller):
        """Test interaction type classification"""
        assert memory_controller._classify_interaction_type("I took my pills") == "health"
        assert memory_controller._classify_interaction_type("I feel sad") == "emotion"
        assert memory_controller._classify_interaction_type("I remember yesterday") == "event"
        assert memory_controller._classify_interaction_type("I like gardening") == "preference"
        assert memory_controller._classify_interaction_type("Hello there") == "interaction"
    
    def test_extract_tags(self, memory_controller):
        """Test tag extraction from interactions"""
        tags = memory_controller._extract_tags(
            "I have a doctor appointment tomorrow morning",
            "I'll remind you about your appointment"
        )
        
        assert "doctor" in tags
        assert "appointment" in tags
        assert "daily" in tags
        
        # Test emotion tags
        tags = memory_controller._extract_tags(
            "I feel happy today",
            "That's wonderful to hear!"
        )
        assert "happy" in tags
        
        # Test memory tags
        tags = memory_controller._extract_tags(
            "Remember yesterday we talked",
            "Yes, I remember"
        )
        assert "memory" in tags
    
    def test_format_context_complete(self, memory_controller):
        """Test context formatting with all components"""
        user_profile = UserProfile(
            user_id="test_user",
            name="Jane Smith",
            age=80,
            conditions=["arthritis"],
            interests=["cooking", "music"]
        )
        
        recent_interactions = "User: How are you?\nAI: I'm well!"
        relevant_memories = [
            {"content": "Loves Italian cooking", "score": 0.92},
            {"content": "Plays piano", "score": 0.85}
        ]
        recent_fragments = [
            MemoryFragment(
                user_id="test_user",
                timestamp=datetime.utcnow(),
                type="preference",
                content="Mentioned enjoying pasta recipes",
                tags=["cooking"],
                retention="active"
            )
        ]
        
        context = memory_controller._format_context(
            user_profile=user_profile,
            recent_interactions=recent_interactions,
            relevant_memories=relevant_memories,
            recent_fragments=recent_fragments,
            user_message="Can you suggest a recipe?"
        )
        
        # Verify all sections are present
        assert "Jane Smith" in context
        assert "Age: 80" in context
        assert "arthritis" in context
        assert "cooking, music" in context
        assert "How are you?" in context
        assert "Loves Italian cooking" in context
        assert "pasta recipes" in context
        assert "Can you suggest a recipe?" in context
        assert "caring AI companion" in context
    
    def test_format_context_minimal(self, memory_controller):
        """Test context formatting with minimal data"""
        user_profile = UserProfile(
            user_id="test_user",
            name="User",
            age=0,
            conditions=[],
            interests=[]
        )
        
        context = memory_controller._format_context(
            user_profile=user_profile,
            recent_interactions="",
            relevant_memories=[],
            recent_fragments=[],
            user_message="Hello"
        )
        
        assert "None recorded" in context  # For conditions and interests
        assert "first conversation today" in context
        assert "No specific relevant memories" in context
        assert "No recent events recorded" in context