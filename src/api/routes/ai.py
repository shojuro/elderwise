from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uuid
from datetime import datetime
import logging

from src.memory.controller import MemoryController
from src.ai.client import ai_client
from src.models.memory import InteractionLog

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize controller
memory_controller = MemoryController()


class ChatRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    message: str = Field(..., description="User's message")
    session_id: Optional[str] = Field(None, description="Session identifier")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(500, ge=50, le=2000)
    stream: Optional[bool] = Field(False, description="Enable streaming response")


class ChatResponse(BaseModel):
    response: str
    session_id: str
    response_time_ms: int
    context_summary: Dict[str, Any]


@router.post("/respond", response_model=ChatResponse)
async def generate_response(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Main endpoint for AI responses with memory integration
    
    This endpoint:
    1. Assembles context from all memory sources
    2. Sends context to Mistral 7B for response generation
    3. Stores the interaction back to memory
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Step 1: Assemble context from memory
        logger.info(f"Assembling context for user {request.user_id}")
        context = await memory_controller.assemble_context(
            user_id=request.user_id,
            user_message=request.message
        )
        
        # Step 2: Generate AI response
        logger.info(f"Generating response for user {request.user_id}")
        response_data = await ai_client.generate_response(
            context=context["context_string"],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            user_id=request.user_id,
            session_id=session_id
        )
        
        if not response_data.success:
            raise HTTPException(status_code=500, detail="Failed to generate response")
        
        ai_response = response_data.response
        response_time_ms = response_data.response_time_ms
        
        # Step 3: Store interaction in background
        background_tasks.add_task(
            store_interaction_background,
            user_id=request.user_id,
            session_id=session_id,
            user_message=request.message,
            ai_response=ai_response,
            context_used=context,
            response_time_ms=response_time_ms
        )
        
        # Prepare context summary for response
        context_summary = {
            "profile_loaded": bool(context.get("user_profile")),
            "recent_interactions_count": len(context.get("recent_interactions", "").split("\n")),
            "relevant_memories_count": len(context.get("relevant_memories", [])),
            "recent_fragments_count": len(context.get("recent_fragments", []))
        }
        
        return ChatResponse(
            response=ai_response,
            session_id=session_id,
            response_time_ms=response_time_ms,
            context_summary=context_summary
        )
        
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/respond/stream")
async def generate_streaming_response(request: ChatRequest):
    """
    Streaming endpoint for AI responses
    
    Returns server-sent events stream
    """
    try:
        # Assemble context
        context = await memory_controller.assemble_context(
            user_id=request.user_id,
            user_message=request.message
        )
        
        # Generate streaming response
        async def event_generator():
            async for chunk in ai_client.generate_streaming_response(
                context=context["context_string"],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                user_id=request.user_id,
                session_id=request.session_id or str(uuid.uuid4())
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        logger.error(f"Error in streaming response: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def store_interaction_background(user_id: str, session_id: str, user_message: str,
                                      ai_response: str, context_used: Dict[str, Any],
                                      response_time_ms: int):
    """Background task to store interaction data"""
    try:
        # Store in memory controller (handles Redis, MongoDB, and Pinecone)
        await memory_controller.store_interaction(
            user_id=user_id,
            user_message=user_message,
            ai_response=ai_response,
            context_used=context_used,
            response_time_ms=response_time_ms
        )
        
        # Also log the full interaction
        interaction_log = InteractionLog(
            user_id=user_id,
            session_id=session_id,
            timestamp=datetime.utcnow(),
            user_message=user_message,
            ai_response=ai_response,
            context_used=context_used,
            response_time_ms=response_time_ms
        )
        
        await memory_controller.storage.log_interaction(interaction_log)
        
        logger.info(f"Stored interaction for user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to store interaction: {e}")


@router.get("/validate")
async def validate_system():
    """Validate that all components are working"""
    validation_results = {
        "ai_client": False,
        "memory_controller": False,
        "inference": False
    }
    
    try:
        # Check AI client health
        ai_health = await ai_client.health_check()
        validation_results["ai_client"] = ai_health["overall_status"] in ["healthy", "degraded"]
        
        # Check memory controller
        test_context = await memory_controller.assemble_context("test_user", "Hello")
        validation_results["memory_controller"] = bool(test_context.get("context_string"))
        
        # Check inference
        if validation_results["ai_client"]:
            test_response = await ai_client.generate_response("Hello", max_tokens=10)
            validation_results["inference"] = test_response.success
        
    except Exception as e:
        logger.error(f"Validation error: {e}")
    
    return {
        "status": "operational" if all(validation_results.values()) else "degraded",
        "components": validation_results,
        "ai_health": ai_health if 'ai_health' in locals() else None
    }