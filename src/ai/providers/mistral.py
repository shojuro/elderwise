from typing import AsyncGenerator, Dict, Any
from huggingface_hub import InferenceClient
import time
import logging
from src.ai.base import (
    AIProviderInterface,
    AIRequest,
    AIResponse,
    AIProvider,
    ProviderConfig,
    AIProviderConnectionError,
    AIProviderAuthenticationError,
    AIProviderResponseError
)

logger = logging.getLogger(__name__)


class MistralProvider(AIProviderInterface):
    """Mistral AI provider using Hugging Face Inference API"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = None
        self.model_id = config.model_id or "mistralai/Mistral-7B-Instruct-v0.3"
    
    async def initialize(self) -> None:
        """Initialize the Hugging Face Inference Client"""
        try:
            if not self.config.api_key:
                raise AIProviderAuthenticationError("HuggingFace token not provided")
            
            self.client = InferenceClient(
                token=self.config.api_key,
                timeout=self.config.timeout
            )
            
            # Validate the connection
            if await self.validate_connection():
                self._initialized = True
                logger.info(f"Initialized Mistral provider with model {self.model_id}")
            else:
                raise AIProviderConnectionError("Failed to validate Mistral connection")
                
        except Exception as e:
            logger.error(f"Failed to initialize Mistral provider: {e}")
            raise AIProviderConnectionError(f"Failed to initialize: {str(e)}")
    
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generate a response using Mistral"""
        if not self._initialized:
            await self.initialize()
        
        start_time = time.time()
        
        try:
            # Format as chat completion
            messages = [
                {
                    "role": "system",
                    "content": "You are a caring AI companion with persistent memory, supporting elderly users with empathy and understanding."
                },
                {
                    "role": "user",
                    "content": request.context
                }
            ]
            
            # Generate response
            response = self.client.chat_completion(
                messages=messages,
                model=self.model_id,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=False
            )
            
            # Extract response
            ai_response = response.choices[0].message.content
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Extract usage if available
            usage = None
            if hasattr(response, 'usage'):
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            
            logger.info(f"Generated Mistral response in {response_time_ms}ms")
            
            return AIResponse(
                response=ai_response,
                provider=AIProvider.MISTRAL,
                model=self.model_id,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                response_time_ms=response_time_ms,
                success=True,
                usage=usage,
                metadata=request.metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to generate Mistral response: {e}")
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Return a fallback response
            return AIResponse(
                response="I apologize, but I'm having trouble processing that right now. Could you please try again?",
                provider=AIProvider.MISTRAL,
                model=self.model_id,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                response_time_ms=response_time_ms,
                success=False,
                error=str(e)
            )
    
    async def generate_streaming_response(
        self, request: AIRequest
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response using Mistral"""
        if not self._initialized:
            await self.initialize()
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a caring AI companion with persistent memory, supporting elderly users with empathy and understanding."
                },
                {
                    "role": "user",
                    "content": request.context
                }
            ]
            
            # Generate streaming response
            stream = self.client.chat_completion(
                messages=messages,
                model=self.model_id,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Failed to generate streaming response: {e}")
            yield f"I apologize, but I'm having trouble responding right now."
    
    async def validate_connection(self) -> bool:
        """Validate that the HF token has proper access"""
        try:
            if not self.client:
                return False
                
            # Try a minimal request to validate token
            test_response = self.client.chat_completion(
                messages=[{"role": "user", "content": "Hello"}],
                model=self.model_id,
                max_tokens=10
            )
            return True
        except Exception as e:
            logger.error(f"Mistral connection validation failed: {e}")
            return False
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "model_id": self.model_id,
            "provider": "Hugging Face Inference API",
            "type": "chat",
            "context_length": 32768,  # Mistral 7B v0.3 context
            "capabilities": ["chat", "streaming", "instruction_following"]
        }