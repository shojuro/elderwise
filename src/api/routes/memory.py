from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.memory.storage import MemoryStorage
from src.memory.semantic import SemanticMemory
from src.memory.session import SessionManager
from src.models.memory import MemoryFragment

router = APIRouter()
storage = MemoryStorage()
semantic = SemanticMemory()
session = SessionManager()


class CreateMemoryRequest(BaseModel):
    user_id: str
    content: str
    type: str = Field(..., pattern="^(interaction|health|emotion|event|preference)$")
    tags: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SearchMemoryRequest(BaseModel):
    user_id: str
    query: str
    top_k: Optional[int] = Field(5, ge=1, le=20)
    retention: Optional[str] = Field(None, pattern="^(active|archive)$")


@router.post("/create")
async def create_memory(request: CreateMemoryRequest):
    """Manually create a memory fragment"""
    try:
        # Create memory fragment
        fragment = MemoryFragment(
            user_id=request.user_id,
            timestamp=datetime.utcnow(),
            type=request.type,
            content=request.content,
            tags=request.tags,
            retention="active",
            metadata=request.metadata
        )
        
        # Store in MongoDB
        fragment_id = await storage.store_memory_fragment(fragment)
        
        # Store in Pinecone
        vector_id = await semantic.store_memory_vector(
            user_id=request.user_id,
            content=request.content,
            metadata={
                "type": request.type,
                "tags": request.tags,
                "retention": "active",
                "fragment_id": fragment_id,
                **request.metadata
            }
        )
        
        return {
            "message": "Memory created successfully",
            "fragment_id": fragment_id,
            "vector_id": vector_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_memories(request: SearchMemoryRequest):
    """Search for memories using semantic similarity"""
    try:
        memories = await semantic.search_memories(
            user_id=request.user_id,
            query=request.query,
            top_k=request.top_k,
            retention=request.retention
        )
        
        return {
            "query": request.query,
            "results": memories,
            "count": len(memories)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/recent")
async def get_recent_memories(
    user_id: str,
    limit: int = Query(10, ge=1, le=50)
):
    """Get recent memory fragments for a user"""
    try:
        memories = await storage.get_active_memories(user_id, limit=limit)
        
        return {
            "user_id": user_id,
            "memories": [m.model_dump() for m in memories],
            "count": len(memories)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/session")
async def get_session_history(
    user_id: str,
    limit: Optional[int] = Query(None, ge=1, le=20)
):
    """Get recent session interactions from Redis"""
    try:
        interactions = session.get_recent_interactions(user_id, limit=limit)
        
        return {
            "user_id": user_id,
            "interactions": interactions,
            "count": len(interactions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}/session")
async def clear_session(user_id: str):
    """Clear session history for a user"""
    try:
        session.clear_session(user_id)
        
        return {
            "message": "Session cleared successfully",
            "user_id": user_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/archive")
async def trigger_archive():
    """Manually trigger memory archival process"""
    try:
        count = await storage.archive_old_memories()
        
        return {
            "message": "Archive process completed",
            "memories_archived": count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/tags")
async def get_memory_tags(user_id: str):
    """Get all unique tags used in a user's memories"""
    try:
        # Get all memories
        memories = await storage.get_active_memories(user_id, limit=1000)
        
        # Extract unique tags
        all_tags = set()
        for memory in memories:
            all_tags.update(memory.tags)
        
        return {
            "user_id": user_id,
            "tags": sorted(list(all_tags)),
            "count": len(all_tags)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))