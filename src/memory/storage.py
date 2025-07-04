from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from src.utils.database import mongodb_manager
from src.models.memory import UserProfile, MemoryFragment, InteractionLog
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class MemoryStorage:
    def __init__(self):
        self.db = mongodb_manager
        
    async def create_user_profile(self, user_profile: UserProfile) -> str:
        """Create a new user profile"""
        try:
            collection = self.db.get_collection("user_profiles")
            result = await collection.insert_one(user_profile.model_dump())
            logger.info(f"Created user profile for {user_profile.user_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to create user profile: {e}")
            raise
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by user_id"""
        try:
            collection = self.db.get_collection("user_profiles")
            doc = await collection.find_one({"user_id": user_id})
            if doc:
                doc.pop("_id", None)
                return UserProfile(**doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return None
    
    async def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user profile"""
        try:
            collection = self.db.get_collection("user_profiles")
            updates["updated_at"] = datetime.utcnow()
            result = await collection.update_one(
                {"user_id": user_id},
                {"$set": updates}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
            return False
    
    async def store_memory_fragment(self, fragment: MemoryFragment) -> str:
        """Store a new memory fragment"""
        try:
            collection = self.db.get_collection("memory_fragments")
            result = await collection.insert_one(fragment.model_dump())
            logger.info(f"Stored memory fragment for user {fragment.user_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to store memory fragment: {e}")
            raise
    
    async def get_active_memories(self, user_id: str, limit: int = 50) -> List[MemoryFragment]:
        """Get active memory fragments for a user"""
        try:
            collection = self.db.get_collection("memory_fragments")
            cursor = collection.find(
                {"user_id": user_id, "retention": "active"}
            ).sort("timestamp", -1).limit(limit)
            
            memories = []
            async for doc in cursor:
                doc.pop("_id", None)
                memories.append(MemoryFragment(**doc))
            return memories
        except Exception as e:
            logger.error(f"Failed to get active memories: {e}")
            return []
    
    async def search_memories_by_tags(self, user_id: str, tags: List[str], retention: Optional[str] = None) -> List[MemoryFragment]:
        """Search memory fragments by tags"""
        try:
            collection = self.db.get_collection("memory_fragments")
            query = {"user_id": user_id, "tags": {"$in": tags}}
            if retention:
                query["retention"] = retention
                
            cursor = collection.find(query).sort("timestamp", -1)
            
            memories = []
            async for doc in cursor:
                doc.pop("_id", None)
                memories.append(MemoryFragment(**doc))
            return memories
        except Exception as e:
            logger.error(f"Failed to search memories by tags: {e}")
            return []
    
    async def archive_old_memories(self) -> int:
        """Archive memories older than active period"""
        try:
            collection = self.db.get_collection("memory_fragments")
            cutoff_date = datetime.utcnow() - timedelta(days=settings.memory_active_days)
            
            result = await collection.update_many(
                {
                    "retention": "active",
                    "timestamp": {"$lt": cutoff_date}
                },
                {"$set": {"retention": "archive"}}
            )
            
            logger.info(f"Archived {result.modified_count} memory fragments")
            return result.modified_count
        except Exception as e:
            logger.error(f"Failed to archive memories: {e}")
            return 0
    
    async def log_interaction(self, log: InteractionLog) -> str:
        """Log an interaction"""
        try:
            collection = self.db.get_collection("interaction_logs")
            result = await collection.insert_one(log.model_dump())
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to log interaction: {e}")
            raise
    
    async def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get usage statistics for a user"""
        try:
            # Count memories
            memories_collection = self.db.get_collection("memory_fragments")
            active_count = await memories_collection.count_documents(
                {"user_id": user_id, "retention": "active"}
            )
            archive_count = await memories_collection.count_documents(
                {"user_id": user_id, "retention": "archive"}
            )
            
            # Count interactions
            logs_collection = self.db.get_collection("interaction_logs")
            interaction_count = await logs_collection.count_documents(
                {"user_id": user_id}
            )
            
            # Get last interaction
            last_interaction = await logs_collection.find_one(
                {"user_id": user_id},
                sort=[("timestamp", -1)]
            )
            
            return {
                "active_memories": active_count,
                "archived_memories": archive_count,
                "total_interactions": interaction_count,
                "last_interaction": last_interaction["timestamp"] if last_interaction else None
            }
        except Exception as e:
            logger.error(f"Failed to get user statistics: {e}")
            return {}