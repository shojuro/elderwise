"""
Integration tests for memory system components working together
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from src.memory.controller import MemoryController
from src.models.memory import UserProfile, MemoryFragment


class TestMemoryIntegration:
    """Integration tests for memory components"""
    
    @pytest.mark.asyncio
    async def test_full_memory_flow(self):
        """Test complete flow: store interaction -> assemble context -> retrieve"""
        with patch('src.memory.controller.SessionManager') as mock_session_cls, \
             patch('src.memory.controller.MemoryStorage') as mock_storage_cls, \
             patch('src.memory.controller.SemanticMemory') as mock_semantic_cls:
            
            # Setup mocks
            mock_session = mock_session_cls.return_value
            mock_storage = mock_storage_cls.return_value
            mock_semantic = mock_semantic_cls.return_value
            
            # Create controller
            controller = MemoryController()
            
            # 1. Store an interaction
            mock_storage.store_memory_fragment = AsyncMock(return_value="fragment_123")
            mock_semantic.store_memory_vector = AsyncMock(return_value="vector_456")
            
            await controller.store_interaction(
                user_id="test_user",
                user_message="I have a doctor's appointment tomorrow at 2pm",
                ai_response="I'll help you remember your appointment tomorrow at 2pm.",
                context_used={},
                response_time_ms=200
            )
            
            # Verify storage calls
            mock_session.add_interaction.assert_called_once()
            mock_storage.store_memory_fragment.assert_called_once()
            mock_semantic.store_memory_vector.assert_called_once()
            
            # 2. Later, assemble context for a related query
            mock_storage.get_user_profile = AsyncMock(return_value=UserProfile(
                user_id="test_user",
                name="John",
                age=75,
                conditions=["hypertension"],
                interests=[]
            ))
            
            mock_session.format_recent_context.return_value = """
User: I have a doctor's appointment tomorrow at 2pm
AI: I'll help you remember your appointment tomorrow at 2pm.
"""
            
            mock_semantic.search_memories = AsyncMock(return_value=[
                {
                    "content": "User: I have a doctor's appointment tomorrow at 2pm",
                    "score": 0.98,
                    "type": "event",
                    "tags": ["appointment", "doctor"]
                }
            ])
            
            mock_storage.get_active_memories = AsyncMock(return_value=[
                MemoryFragment(
                    user_id="test_user",
                    timestamp=datetime.utcnow() - timedelta(hours=1),
                    type="event",
                    content="Doctor appointment tomorrow at 2pm",
                    tags=["appointment", "doctor"],
                    retention="active"
                )
            ])
            
            # Assemble context
            context = await controller.assemble_context(
                user_id="test_user",
                user_message="What time is my appointment?"
            )
            
            # Verify context contains relevant information
            assert "John" in context["context_string"]
            assert "hypertension" in context["context_string"]
            assert "doctor's appointment" in context["context_string"]
            assert "2pm" in context["context_string"]
            assert len(context["relevant_memories"]) == 1
            assert context["relevant_memories"][0]["score"] == 0.98
    
    @pytest.mark.asyncio
    async def test_memory_classification_and_tagging(self):
        """Test that different types of interactions are classified correctly"""
        with patch('src.memory.controller.SessionManager'), \
             patch('src.memory.controller.MemoryStorage') as mock_storage_cls, \
             patch('src.memory.controller.SemanticMemory') as mock_semantic_cls:
            
            mock_storage = mock_storage_cls.return_value
            mock_semantic = mock_semantic_cls.return_value
            
            controller = MemoryController()
            
            # Test health-related interaction
            mock_storage.store_memory_fragment = AsyncMock()
            mock_semantic.store_memory_vector = AsyncMock()
            
            await controller.store_interaction(
                user_id="test_user",
                user_message="I forgot to take my blood pressure medication this morning",
                ai_response="It's important to take your medication. Would you like me to help set reminders?",
                context_used={},
                response_time_ms=150
            )
            
            # Check the stored fragment
            fragment_call = mock_storage.store_memory_fragment.call_args[0][0]
            assert fragment_call.type == "health"
            assert "medication" in fragment_call.tags
            
            # Test emotion-related interaction
            await controller.store_interaction(
                user_id="test_user",
                user_message="I've been feeling very lonely lately since my daughter moved away",
                ai_response="I understand how difficult that must be. Would you like to talk about it?",
                context_used={},
                response_time_ms=180
            )
            
            fragment_call = mock_storage.store_memory_fragment.call_args[0][0]
            assert fragment_call.type == "emotion"
            assert "lonely" in fragment_call.tags
    
    @pytest.mark.asyncio
    async def test_memory_archival_process(self):
        """Test the memory archival process for old memories"""
        with patch('src.memory.storage.mongodb_manager') as mock_db:
            from src.memory.storage import MemoryStorage
            
            mock_collection = MagicMock()
            mock_db.get_collection.return_value = mock_collection
            
            # Setup mock to return count of updated documents
            mock_collection.update_many = AsyncMock()
            mock_collection.update_many.return_value.modified_count = 10
            
            storage = MemoryStorage()
            
            # Archive old memories
            with patch('src.memory.storage.settings') as mock_settings:
                mock_settings.memory_active_days = 90
                archived_count = await storage.archive_old_memories()
            
            assert archived_count == 10
            
            # Verify the query
            update_call = mock_collection.update_many.call_args[0]
            query = update_call[0]
            update = update_call[1]
            
            assert query["retention"] == "active"
            assert "$lt" in query["timestamp"]
            assert update["$set"]["retention"] == "archive"
    
    @pytest.mark.asyncio
    async def test_context_assembly_priority(self):
        """Test that context assembly prioritizes recent and relevant memories"""
        with patch('src.memory.controller.SessionManager') as mock_session_cls, \
             patch('src.memory.controller.MemoryStorage') as mock_storage_cls, \
             patch('src.memory.controller.SemanticMemory') as mock_semantic_cls:
            
            mock_semantic = mock_semantic_cls.return_value
            mock_storage = mock_storage_cls.return_value
            
            controller = MemoryController()
            
            # Setup user profile
            mock_storage.get_user_profile = AsyncMock(return_value=UserProfile(
                user_id="test_user",
                name="Mary",
                age=80,
                conditions=[],
                interests=["cooking"]
            ))
            
            # Setup semantic search to return memories sorted by relevance
            mock_semantic.search_memories = AsyncMock(return_value=[
                {"content": "Loves Italian cooking", "score": 0.95, "tags": ["cooking"]},
                {"content": "Mentioned pasta recipes", "score": 0.90, "tags": ["cooking", "italian"]},
                {"content": "Enjoys gardening", "score": 0.60, "tags": ["hobby"]},
                {"content": "Takes daily walks", "score": 0.40, "tags": ["health"]},
                {"content": "Watches TV in evening", "score": 0.30, "tags": ["routine"]}
            ])
            
            # Recent memories from MongoDB
            now = datetime.utcnow()
            mock_storage.get_active_memories = AsyncMock(return_value=[
                MemoryFragment(
                    user_id="test_user",
                    timestamp=now - timedelta(hours=1),
                    type="preference",
                    content="Made lasagna for dinner",
                    tags=["cooking"],
                    retention="active"
                ),
                MemoryFragment(
                    user_id="test_user",
                    timestamp=now - timedelta(days=1),
                    type="event",
                    content="Visited the farmer's market",
                    tags=["shopping"],
                    retention="active"
                )
            ])
            
            mock_session_cls.return_value.format_recent_context.return_value = "Recent chat history"
            
            # Query about cooking
            context = await controller.assemble_context(
                user_id="test_user",
                user_message="Can you suggest an Italian recipe?"
            )
            
            # Verify context includes most relevant memories
            context_string = context["context_string"]
            assert "Italian cooking" in context_string
            assert "lasagna" in context_string
            assert "Mary" in context_string
            
            # Check that only top 3 semantic memories are included in formatted context
            assert context_string.count("Relevance:") == 3