from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.models.memory import UserProfile
from src.memory.storage import MemoryStorage

router = APIRouter()
storage = MemoryStorage()


class CreateUserRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    name: str = Field(..., description="User's name")
    age: int = Field(..., ge=0, le=150, description="User's age")
    conditions: Optional[List[str]] = Field(default_factory=list, description="Health conditions")
    interests: Optional[List[str]] = Field(default_factory=list, description="User interests")


class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    conditions: Optional[List[str]] = None
    interests: Optional[List[str]] = None


@router.post("/create")
async def create_user(request: CreateUserRequest):
    """Create a new user profile"""
    try:
        # Check if user already exists
        existing_user = await storage.get_user_profile(request.user_id)
        if existing_user:
            raise HTTPException(status_code=409, detail="User already exists")
        
        # Create new profile
        user_profile = UserProfile(
            user_id=request.user_id,
            name=request.name,
            age=request.age,
            conditions=request.conditions,
            interests=request.interests
        )
        
        profile_id = await storage.create_user_profile(user_profile)
        
        return {
            "message": "User profile created successfully",
            "user_id": request.user_id,
            "profile_id": profile_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}")
async def get_user(user_id: str):
    """Get user profile by ID"""
    try:
        user_profile = await storage.get_user_profile(user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user_profile.model_dump()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}")
async def update_user(user_id: str, request: UpdateUserRequest):
    """Update user profile"""
    try:
        # Check if user exists
        existing_user = await storage.get_user_profile(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prepare updates
        updates = request.model_dump(exclude_unset=True)
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        # Update profile
        success = await storage.update_user_profile(user_id, updates)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update user profile")
        
        # Return updated profile
        updated_profile = await storage.get_user_profile(user_id)
        
        return {
            "message": "User profile updated successfully",
            "profile": updated_profile.model_dump()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/stats")
async def get_user_stats(user_id: str):
    """Get user statistics including memory and interaction counts"""
    try:
        # Check if user exists
        user_profile = await storage.get_user_profile(user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get statistics
        stats = await storage.get_user_statistics(user_id)
        
        return {
            "user_id": user_id,
            "name": user_profile.name,
            "statistics": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))