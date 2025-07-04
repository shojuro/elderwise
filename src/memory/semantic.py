from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from src.utils.database import pinecone_manager
from src.utils.embeddings import embedding_service
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class SemanticMemory:
    def __init__(self):
        self.index = pinecone_manager.get_index()
        self.embeddings = embedding_service
        
    def _generate_id(self) -> str:
        """Generate unique ID for vector"""
        return str(uuid.uuid4())
    
    async def store_memory_vector(self, user_id: str, content: str, metadata: Dict[str, Any]) -> str:
        """Store a memory fragment as a vector"""
        try:
            # Generate embedding
            embedding = self.embeddings.embed(content)
            
            # Generate unique ID
            vector_id = self._generate_id()
            
            # Prepare metadata
            vector_metadata = {
                "user_id": user_id,
                "content": content[:1000],  # Truncate for metadata limits
                "timestamp": datetime.utcnow().isoformat(),
                **metadata
            }
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[(vector_id, embedding, vector_metadata)]
            )
            
            logger.info(f"Stored semantic memory for user {user_id}")
            return vector_id
        except Exception as e:
            logger.error(f"Failed to store memory vector: {e}")
            raise
    
    async def search_memories(self, user_id: str, query: str, top_k: int = 5, 
                            retention: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for relevant memories based on semantic similarity"""
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed(query)
            
            # Build filter
            filter_dict = {"user_id": {"$eq": user_id}}
            if retention:
                filter_dict["retention"] = {"$eq": retention}
            
            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            # Format results
            memories = []
            for match in results.matches:
                memory = {
                    "id": match.id,
                    "score": match.score,
                    "content": match.metadata.get("content", ""),
                    "timestamp": match.metadata.get("timestamp", ""),
                    "tags": match.metadata.get("tags", []),
                    "type": match.metadata.get("type", ""),
                    "metadata": match.metadata
                }
                memories.append(memory)
            
            return memories
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
    
    async def update_memory_retention(self, vector_ids: List[str], retention: str):
        """Update retention status for memory vectors"""
        try:
            # Fetch existing vectors
            fetch_result = self.index.fetch(ids=vector_ids)
            
            # Update metadata
            vectors_to_update = []
            for vector_id, vector_data in fetch_result.vectors.items():
                if vector_data:
                    metadata = vector_data.metadata
                    metadata["retention"] = retention
                    vectors_to_update.append(
                        (vector_id, vector_data.values, metadata)
                    )
            
            # Upsert updated vectors
            if vectors_to_update:
                self.index.upsert(vectors=vectors_to_update)
                logger.info(f"Updated retention for {len(vectors_to_update)} vectors")
                
        except Exception as e:
            logger.error(f"Failed to update memory retention: {e}")
    
    async def delete_memories(self, vector_ids: List[str]):
        """Delete memory vectors"""
        try:
            self.index.delete(ids=vector_ids)
            logger.info(f"Deleted {len(vector_ids)} memory vectors")
        except Exception as e:
            logger.error(f"Failed to delete memories: {e}")
    
    async def get_memory_stats(self, user_id: str) -> Dict[str, Any]:
        """Get statistics about user's semantic memories"""
        try:
            # Query with dummy vector to get count
            dummy_vector = [0.0] * 384
            
            active_results = self.index.query(
                vector=dummy_vector,
                top_k=1,
                filter={
                    "user_id": {"$eq": user_id},
                    "retention": {"$eq": "active"}
                }
            )
            
            archive_results = self.index.query(
                vector=dummy_vector,
                top_k=1,
                filter={
                    "user_id": {"$eq": user_id},
                    "retention": {"$eq": "archive"}
                }
            )
            
            return {
                "active_vectors": len(active_results.matches),
                "archive_vectors": len(archive_results.matches)
            }
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {"active_vectors": 0, "archive_vectors": 0}