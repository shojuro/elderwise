import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import uuid
from src.memory.semantic import SemanticMemory


class TestSemanticMemory:
    """Test cases for SemanticMemory"""
    
    @pytest.fixture
    def mock_index(self):
        """Create a mock Pinecone index"""
        index = MagicMock()
        index.upsert = Mock()
        index.query = Mock()
        index.fetch = Mock()
        index.delete = Mock()
        return index
    
    @pytest.fixture
    def mock_embeddings(self):
        """Create a mock embedding service"""
        embeddings = MagicMock()
        # Return a 384-dimensional vector (for all-MiniLM-L6-v2)
        embeddings.embed = Mock(return_value=[0.1] * 384)
        return embeddings
    
    @pytest.fixture
    def semantic_memory(self, mock_index, mock_embeddings):
        """Create a SemanticMemory instance with mocked dependencies"""
        with patch('src.memory.semantic.pinecone_manager') as mock_pinecone, \
             patch('src.memory.semantic.embedding_service', mock_embeddings):
            
            mock_pinecone.get_index.return_value = mock_index
            memory = SemanticMemory()
            return memory
    
    def test_generate_id(self, semantic_memory):
        """Test ID generation"""
        id1 = semantic_memory._generate_id()
        id2 = semantic_memory._generate_id()
        
        # Should be valid UUIDs
        assert uuid.UUID(id1)
        assert uuid.UUID(id2)
        
        # Should be unique
        assert id1 != id2
    
    @pytest.mark.asyncio
    async def test_store_memory_vector_success(self, semantic_memory, mock_index, mock_embeddings):
        """Test storing a memory vector successfully"""
        # Execute
        vector_id = await semantic_memory.store_memory_vector(
            user_id="test_user",
            content="I took my medication this morning",
            metadata={"type": "health", "tags": ["medication"]}
        )
        
        # Assert
        assert uuid.UUID(vector_id)  # Should be a valid UUID
        mock_embeddings.embed.assert_called_once_with("I took my medication this morning")
        mock_index.upsert.assert_called_once()
        
        # Check upsert arguments
        upsert_call = mock_index.upsert.call_args[1]["vectors"][0]
        assert len(upsert_call) == 3  # (id, embedding, metadata)
        assert upsert_call[0] == vector_id
        assert len(upsert_call[1]) == 384  # Embedding dimension
        
        metadata = upsert_call[2]
        assert metadata["user_id"] == "test_user"
        assert metadata["content"] == "I took my medication this morning"
        assert metadata["type"] == "health"
        assert metadata["tags"] == ["medication"]
        assert "timestamp" in metadata
    
    @pytest.mark.asyncio
    async def test_store_memory_vector_long_content(self, semantic_memory, mock_index):
        """Test storing memory with content that exceeds metadata limit"""
        long_content = "x" * 2000  # Longer than 1000 char limit
        
        vector_id = await semantic_memory.store_memory_vector(
            user_id="test_user",
            content=long_content,
            metadata={}
        )
        
        # Check that content was truncated in metadata
        upsert_call = mock_index.upsert.call_args[1]["vectors"][0]
        metadata = upsert_call[2]
        assert len(metadata["content"]) == 1000
        assert metadata["content"] == "x" * 1000
    
    @pytest.mark.asyncio
    async def test_store_memory_vector_error(self, semantic_memory, mock_index):
        """Test error handling when storing vector fails"""
        mock_index.upsert.side_effect = Exception("Pinecone error")
        
        with pytest.raises(Exception):
            await semantic_memory.store_memory_vector(
                user_id="test_user",
                content="Test content",
                metadata={}
            )
    
    @pytest.mark.asyncio
    async def test_search_memories_success(self, semantic_memory, mock_index, mock_embeddings):
        """Test searching memories successfully"""
        # Setup mock query results
        mock_match1 = MagicMock()
        mock_match1.id = "vector1"
        mock_match1.score = 0.95
        mock_match1.metadata = {
            "content": "Memory about medication",
            "timestamp": "2024-01-01T10:00:00",
            "tags": ["health", "medication"],
            "type": "health",
            "user_id": "test_user"
        }
        
        mock_match2 = MagicMock()
        mock_match2.id = "vector2"
        mock_match2.score = 0.87
        mock_match2.metadata = {
            "content": "Memory about doctor visit",
            "timestamp": "2024-01-02T14:00:00",
            "tags": ["health", "appointment"],
            "type": "event",
            "user_id": "test_user"
        }
        
        mock_results = MagicMock()
        mock_results.matches = [mock_match1, mock_match2]
        mock_index.query.return_value = mock_results
        
        # Execute
        memories = await semantic_memory.search_memories(
            user_id="test_user",
            query="Tell me about my health",
            top_k=5,
            retention="active"
        )
        
        # Assert
        assert len(memories) == 2
        assert memories[0]["id"] == "vector1"
        assert memories[0]["score"] == 0.95
        assert memories[0]["content"] == "Memory about medication"
        assert memories[0]["type"] == "health"
        assert "medication" in memories[0]["tags"]
        
        # Check query call
        mock_embeddings.embed.assert_called_once_with("Tell me about my health")
        mock_index.query.assert_called_once()
        query_args = mock_index.query.call_args[1]
        assert query_args["top_k"] == 5
        assert query_args["include_metadata"] is True
        assert query_args["filter"]["user_id"]["$eq"] == "test_user"
        assert query_args["filter"]["retention"]["$eq"] == "active"
    
    @pytest.mark.asyncio
    async def test_search_memories_no_retention_filter(self, semantic_memory, mock_index):
        """Test searching without retention filter"""
        mock_results = MagicMock()
        mock_results.matches = []
        mock_index.query.return_value = mock_results
        
        await semantic_memory.search_memories(
            user_id="test_user",
            query="test query",
            top_k=10
        )
        
        # Check that retention filter was not included
        query_args = mock_index.query.call_args[1]
        assert "retention" not in query_args["filter"]
        assert query_args["filter"]["user_id"]["$eq"] == "test_user"
    
    @pytest.mark.asyncio
    async def test_search_memories_error(self, semantic_memory, mock_index):
        """Test error handling when search fails"""
        mock_index.query.side_effect = Exception("Pinecone error")
        
        memories = await semantic_memory.search_memories(
            user_id="test_user",
            query="test query"
        )
        
        # Should return empty list on error
        assert memories == []
    
    @pytest.mark.asyncio
    async def test_update_memory_retention(self, semantic_memory, mock_index):
        """Test updating memory retention status"""
        # Setup mock fetch results
        mock_vector1 = MagicMock()
        mock_vector1.values = [0.1] * 384
        mock_vector1.metadata = {"user_id": "test_user", "retention": "active"}
        
        mock_vector2 = MagicMock()
        mock_vector2.values = [0.2] * 384
        mock_vector2.metadata = {"user_id": "test_user", "retention": "active"}
        
        mock_fetch_result = MagicMock()
        mock_fetch_result.vectors = {
            "vector1": mock_vector1,
            "vector2": mock_vector2
        }
        mock_index.fetch.return_value = mock_fetch_result
        
        # Execute
        await semantic_memory.update_memory_retention(
            vector_ids=["vector1", "vector2"],
            retention="archive"
        )
        
        # Assert
        mock_index.fetch.assert_called_once_with(ids=["vector1", "vector2"])
        mock_index.upsert.assert_called_once()
        
        # Check updated vectors
        upsert_vectors = mock_index.upsert.call_args[1]["vectors"]
        assert len(upsert_vectors) == 2
        
        for vector_id, values, metadata in upsert_vectors:
            assert metadata["retention"] == "archive"
    
    @pytest.mark.asyncio
    async def test_update_memory_retention_empty_vectors(self, semantic_memory, mock_index):
        """Test updating retention when some vectors don't exist"""
        mock_fetch_result = MagicMock()
        mock_fetch_result.vectors = {
            "vector1": None,  # Vector doesn't exist
            "vector2": MagicMock(values=[0.1] * 384, metadata={"retention": "active"})
        }
        mock_index.fetch.return_value = mock_fetch_result
        
        await semantic_memory.update_memory_retention(["vector1", "vector2"], "archive")
        
        # Should only update existing vector
        upsert_vectors = mock_index.upsert.call_args[1]["vectors"]
        assert len(upsert_vectors) == 1
    
    @pytest.mark.asyncio
    async def test_delete_memories(self, semantic_memory, mock_index):
        """Test deleting memory vectors"""
        vector_ids = ["vector1", "vector2", "vector3"]
        
        await semantic_memory.delete_memories(vector_ids)
        
        mock_index.delete.assert_called_once_with(ids=vector_ids)
    
    @pytest.mark.asyncio
    async def test_delete_memories_error(self, semantic_memory, mock_index):
        """Test error handling when deletion fails"""
        mock_index.delete.side_effect = Exception("Pinecone error")
        
        # Should not raise exception
        await semantic_memory.delete_memories(["vector1"])
    
    @pytest.mark.asyncio
    async def test_get_memory_stats(self, semantic_memory, mock_index):
        """Test getting memory statistics"""
        # Setup mock results
        mock_active_results = MagicMock()
        mock_active_results.matches = [MagicMock() for _ in range(10)]
        
        mock_archive_results = MagicMock()
        mock_archive_results.matches = [MagicMock() for _ in range(5)]
        
        mock_index.query.side_effect = [mock_active_results, mock_archive_results]
        
        # Execute
        stats = await semantic_memory.get_memory_stats("test_user")
        
        # Assert
        assert stats["active_vectors"] == 10
        assert stats["archive_vectors"] == 5
        
        # Check query calls
        assert mock_index.query.call_count == 2
        
        # First call for active memories
        first_call = mock_index.query.call_args_list[0][1]
        assert first_call["filter"]["user_id"]["$eq"] == "test_user"
        assert first_call["filter"]["retention"]["$eq"] == "active"
        
        # Second call for archive memories
        second_call = mock_index.query.call_args_list[1][1]
        assert second_call["filter"]["user_id"]["$eq"] == "test_user"
        assert second_call["filter"]["retention"]["$eq"] == "archive"
    
    @pytest.mark.asyncio
    async def test_get_memory_stats_error(self, semantic_memory, mock_index):
        """Test error handling when getting stats fails"""
        mock_index.query.side_effect = Exception("Pinecone error")
        
        stats = await semantic_memory.get_memory_stats("test_user")
        
        # Should return zeros on error
        assert stats["active_vectors"] == 0
        assert stats["archive_vectors"] == 0