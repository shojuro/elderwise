from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from bson import ObjectId


class UserProfile(BaseModel):
    user_id: str
    name: str
    age: int
    conditions: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


class MemoryFragment(BaseModel):
    user_id: str
    timestamp: datetime
    type: Literal["interaction", "health", "emotion", "event", "preference"]
    content: str
    tags: List[str] = Field(default_factory=list)
    embedding_id: Optional[str] = None
    retention: Literal["active", "archive"] = "active"
    metadata: dict = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


class InteractionLog(BaseModel):
    user_id: str
    session_id: str
    timestamp: datetime
    user_message: str
    ai_response: str
    context_used: Optional[dict] = None
    response_time_ms: Optional[int] = None
    
    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }