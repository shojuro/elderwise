from typing import AsyncGenerator, Dict, Any
import time
import random
import logging
from src.ai.base import (
    AIProviderInterface,
    AIRequest,
    AIResponse,
    AIProvider,
    ProviderConfig
)

logger = logging.getLogger(__name__)


class MockProvider(AIProviderInterface):
    """Mock AI provider for testing and development"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.responses = [
            "I understand how you're feeling. Is there anything specific I can help you with today?",
            "That's wonderful to hear! Tell me more about that.",
            "I remember you mentioning that before. How has that been going?",
            "Your health is important. Have you been taking your medications as prescribed?",
            "It's great that you're staying active. What activities have you enjoyed recently?",
            "I'm here to listen and support you. Please continue.",
            "That must be challenging. How are you coping with this situation?",
            "Thank you for sharing that with me. Your experiences are valuable.",
        ]
    
    async def initialize(self) -> None:
        """Initialize the mock provider"""
        # Simulate initialization delay
        await asyncio.sleep(0.1)
        self._initialized = True
        logger.info("Initialized Mock AI provider")
    
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generate a mock response"""
        if not self._initialized:
            await self.initialize()
        
        start_time = time.time()
        
        # Simulate processing time based on max_tokens
        processing_time = min(0.5, request.max_tokens / 1000)
        await asyncio.sleep(processing_time)
        
        # Select a response based on context hash for consistency
        context_hash = hash(request.context) % len(self.responses)
        response_text = self.responses[context_hash]
        
        # Add personalization if user_id is provided
        if request.user_id:
            response_text = f"[User {request.user_id}] {response_text}"
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Simulate token usage
        tokens_used = random.randint(50, min(200, request.max_tokens))
        
        return AIResponse(
            response=response_text,
            provider=AIProvider.MOCK,
            model="mock-model-v1",
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            response_time_ms=response_time_ms,
            success=True,
            usage={
                "prompt_tokens": len(request.context.split()),
                "completion_tokens": tokens_used,
                "total_tokens": len(request.context.split()) + tokens_used
            },
            metadata={
                "mock": True,
                **(request.metadata or {})
            }
        )
    
    async def generate_streaming_response(
        self, request: AIRequest
    ) -> AsyncGenerator[str, None]:
        """Generate a mock streaming response"""
        if not self._initialized:
            await self.initialize()
        
        # Select a response
        context_hash = hash(request.context) % len(self.responses)
        response_text = self.responses[context_hash]
        
        # Stream word by word
        words = response_text.split()
        for i, word in enumerate(words):
            await asyncio.sleep(0.05)  # Simulate streaming delay
            if i < len(words) - 1:
                yield word + " "
            else:
                yield word
    
    async def validate_connection(self) -> bool:
        """Always returns True for mock provider"""
        return True
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get mock model information"""
        return {
            "model_id": "mock-model-v1",
            "provider": "Mock Provider",
            "type": "mock",
            "context_length": 8192,
            "capabilities": ["chat", "streaming", "testing"],
            "description": "Mock AI provider for testing and development"
        }


# Add missing import
import asyncio