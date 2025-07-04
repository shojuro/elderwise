from typing import Dict, Any, List, Optional
from datetime import datetime
from src.memory.session import SessionManager
from src.memory.storage import MemoryStorage
from src.memory.semantic import SemanticMemory
from src.models.memory import MemoryFragment, UserProfile
import logging

logger = logging.getLogger(__name__)


class MemoryController:
    def __init__(self):
        self.session = SessionManager()
        self.storage = MemoryStorage()
        self.semantic = SemanticMemory()
    
    async def assemble_context(self, user_id: str, user_message: str) -> Dict[str, Any]:
        """
        Assemble full context from all memory sources
        
        Returns:
            Dictionary containing:
            - user_profile: User profile information
            - recent_interactions: Recent conversation history
            - relevant_memories: Semantically relevant long-term memories
            - context_string: Pre-formatted context for LLM
        """
        try:
            # 1. Get user profile
            user_profile = await self.storage.get_user_profile(user_id)
            if not user_profile:
                logger.warning(f"No profile found for user {user_id}")
                user_profile = UserProfile(
                    user_id=user_id,
                    name="Friend",
                    age=0,
                    conditions=[],
                    interests=[]
                )
            
            # 2. Get recent interactions from Redis
            recent_interactions = self.session.format_recent_context(user_id)
            
            # 3. Search for relevant memories using semantic search
            relevant_memories = await self.semantic.search_memories(
                user_id=user_id,
                query=user_message,
                top_k=5,
                retention="active"  # Only search active memories for context
            )
            
            # 4. Get recent memory fragments from MongoDB
            recent_fragments = await self.storage.get_active_memories(user_id, limit=10)
            
            # 5. Build formatted context string
            context_string = self._format_context(
                user_profile=user_profile,
                recent_interactions=recent_interactions,
                relevant_memories=relevant_memories,
                recent_fragments=recent_fragments,
                user_message=user_message
            )
            
            return {
                "user_profile": user_profile.model_dump(),
                "recent_interactions": recent_interactions,
                "relevant_memories": relevant_memories,
                "recent_fragments": [f.model_dump() for f in recent_fragments],
                "context_string": context_string
            }
            
        except Exception as e:
            logger.error(f"Failed to assemble context: {e}")
            # Return minimal context on error
            return {
                "user_profile": {"user_id": user_id, "name": "Friend"},
                "recent_interactions": "",
                "relevant_memories": [],
                "recent_fragments": [],
                "context_string": f"User says: {user_message}"
            }
    
    def _format_context(self, user_profile: UserProfile, recent_interactions: str,
                       relevant_memories: List[Dict], recent_fragments: List[MemoryFragment],
                       user_message: str) -> str:
        """Format all context into a string for the LLM"""
        
        # User profile section
        profile_text = f"""User Profile:
Name: {user_profile.name}
Age: {user_profile.age}
Health Conditions: {', '.join(user_profile.conditions) if user_profile.conditions else 'None recorded'}
Interests: {', '.join(user_profile.interests) if user_profile.interests else 'None recorded'}"""
        
        # Recent interactions section
        interactions_text = f"""Recent Conversation History:
{recent_interactions if recent_interactions else 'This is our first conversation today.'}"""
        
        # Relevant memories section
        memories_text = "Relevant Long-term Memories:"
        if relevant_memories:
            for memory in relevant_memories[:3]:  # Top 3 most relevant
                memories_text += f"\n- {memory['content']} (Relevance: {memory['score']:.2f})"
        else:
            memories_text += "\nNo specific relevant memories found."
        
        # Recent events section (from MongoDB fragments)
        events_text = "Recent Events and Context:"
        if recent_fragments:
            for fragment in recent_fragments[:5]:
                timestamp = fragment.timestamp.strftime("%Y-%m-%d %H:%M")
                events_text += f"\n- [{timestamp}] {fragment.content}"
        else:
            events_text += "\nNo recent events recorded."
        
        # Combine all sections
        full_context = f"""You are a caring AI companion supporting an elderly user. You have persistent memory and should respond as if you genuinely remember past conversations and care about their wellbeing.

{profile_text}

{interactions_text}

{memories_text}

{events_text}

Current Message: "{user_message}"

Instructions:
- Respond naturally and empathetically
- Reference relevant past information when appropriate
- Show that you remember and care about their situation
- Be supportive and encouraging
- If health concerns are mentioned, gently suggest consulting healthcare providers
- Keep responses conversational and warm"""
        
        return full_context
    
    async def store_interaction(self, user_id: str, user_message: str, ai_response: str,
                              context_used: Dict[str, Any], response_time_ms: int):
        """Store an interaction in all memory systems"""
        try:
            # 1. Add to Redis session
            self.session.add_interaction(user_id, user_message, ai_response)
            
            # 2. Create memory fragment for significant interactions
            if self._is_significant_interaction(user_message, ai_response):
                fragment = MemoryFragment(
                    user_id=user_id,
                    timestamp=datetime.utcnow(),
                    type=self._classify_interaction_type(user_message),
                    content=f"User: {user_message}\nAI: {ai_response}",
                    tags=self._extract_tags(user_message, ai_response),
                    retention="active"
                )
                
                # Store in MongoDB
                fragment_id = await self.storage.store_memory_fragment(fragment)
                
                # Store in Pinecone with metadata
                vector_id = await self.semantic.store_memory_vector(
                    user_id=user_id,
                    content=fragment.content,
                    metadata={
                        "type": fragment.type,
                        "tags": fragment.tags,
                        "retention": fragment.retention,
                        "fragment_id": fragment_id
                    }
                )
                
                # Update fragment with vector ID
                fragment.embedding_id = vector_id
            
            logger.info(f"Stored interaction for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to store interaction: {e}")
    
    def _is_significant_interaction(self, user_message: str, ai_response: str) -> bool:
        """Determine if an interaction is significant enough to store long-term"""
        # Simple heuristics - can be made more sophisticated
        keywords = ["medication", "pain", "feel", "doctor", "appointment", "family",
                   "remember", "forgot", "worried", "happy", "sad", "lonely"]
        
        combined_text = (user_message + " " + ai_response).lower()
        
        # Check for keywords
        has_keywords = any(keyword in combined_text for keyword in keywords)
        
        # Check for length (significant conversations tend to be longer)
        is_substantial = len(user_message.split()) > 10 or len(ai_response.split()) > 20
        
        return has_keywords or is_substantial
    
    def _classify_interaction_type(self, user_message: str) -> str:
        """Classify the type of interaction"""
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["medication", "pill", "doctor", "pain", "hurt"]):
            return "health"
        elif any(word in message_lower for word in ["feel", "sad", "happy", "lonely", "worried"]):
            return "emotion"
        elif any(word in message_lower for word in ["remember", "forgot", "yesterday", "last week"]):
            return "event"
        elif any(word in message_lower for word in ["like", "enjoy", "prefer", "favorite"]):
            return "preference"
        else:
            return "interaction"
    
    def _extract_tags(self, user_message: str, ai_response: str) -> List[str]:
        """Extract relevant tags from the interaction"""
        tags = []
        combined_text = (user_message + " " + ai_response).lower()
        
        # Health tags
        health_terms = ["medication", "doctor", "pain", "appointment", "symptom"]
        tags.extend([term for term in health_terms if term in combined_text])
        
        # Emotion tags
        emotion_terms = ["happy", "sad", "worried", "anxious", "lonely"]
        tags.extend([term for term in emotion_terms if term in combined_text])
        
        # Time tags
        if any(word in combined_text for word in ["today", "morning", "evening"]):
            tags.append("daily")
        if any(word in combined_text for word in ["yesterday", "last week", "remember"]):
            tags.append("memory")
        
        return list(set(tags))  # Remove duplicates