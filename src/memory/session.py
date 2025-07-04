from typing import List, Optional
import json
from datetime import datetime
from src.utils.database import redis_manager
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    def __init__(self):
        self.redis = redis_manager.get_client()
        self.session_ttl = 86400  # 24 hours in seconds
        
    def _get_session_key(self, user_id: str) -> str:
        return f"session:{user_id}:history"
    
    def add_interaction(self, user_id: str, user_message: str, ai_response: str):
        """Add a new interaction to the session history"""
        try:
            key = self._get_session_key(user_id)
            interaction = {
                "timestamp": datetime.utcnow().isoformat(),
                "user": user_message,
                "ai": ai_response
            }
            
            # Add to list
            self.redis.rpush(key, json.dumps(interaction))
            
            # Trim to keep only last N interactions
            self.redis.ltrim(key, -settings.memory_context_limit, -1)
            
            # Reset TTL
            self.redis.expire(key, self.session_ttl)
            
            logger.info(f"Added interaction for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to add interaction: {e}")
            raise
    
    def get_recent_interactions(self, user_id: str, limit: Optional[int] = None) -> List[dict]:
        """Get recent interactions from session history"""
        try:
            key = self._get_session_key(user_id)
            limit = limit or settings.memory_context_limit
            
            # Get last N interactions
            raw_interactions = self.redis.lrange(key, -limit, -1)
            
            interactions = []
            for raw in raw_interactions:
                try:
                    interactions.append(json.loads(raw))
                except json.JSONDecodeError:
                    logger.warning(f"Failed to decode interaction: {raw}")
                    
            return interactions
        except Exception as e:
            logger.error(f"Failed to get interactions: {e}")
            return []
    
    def clear_session(self, user_id: str):
        """Clear session history for a user"""
        try:
            key = self._get_session_key(user_id)
            self.redis.delete(key)
            logger.info(f"Cleared session for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to clear session: {e}")
            raise
    
    def format_recent_context(self, user_id: str) -> str:
        """Format recent interactions as context string"""
        interactions = self.get_recent_interactions(user_id)
        
        if not interactions:
            return "No recent interactions."
        
        context_lines = []
        for interaction in interactions:
            timestamp = interaction.get("timestamp", "")
            user_msg = interaction.get("user", "")
            ai_msg = interaction.get("ai", "")
            
            context_lines.append(f"[{timestamp}]")
            context_lines.append(f"User: {user_msg}")
            context_lines.append(f"AI: {ai_msg}")
            context_lines.append("")
        
        return "\n".join(context_lines)