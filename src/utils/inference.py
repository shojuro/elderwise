from typing import Dict, Any, Optional
from huggingface_hub import InferenceClient
from src.config.settings import settings
import logging
import time

logger = logging.getLogger(__name__)


class MistralInference:
    def __init__(self):
        self.client = None
        self.model_id = "mistralai/Mistral-7B-Instruct-v0.3"
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Hugging Face Inference Client"""
        try:
            self.client = InferenceClient(
                token=settings.hf_token,
                timeout=60  # 60 second timeout
            )
            logger.info(f"Initialized inference client for {self.model_id}")
        except Exception as e:
            logger.error(f"Failed to initialize inference client: {e}")
            raise
    
    async def generate_response(self, context: str, temperature: float = 0.7,
                              max_tokens: int = 500) -> Dict[str, Any]:
        """
        Generate a response using Mistral 7B
        
        Args:
            context: The full context string including user message
            temperature: Control randomness (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dictionary with response and metadata
        """
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
                    "content": context
                }
            ]
            
            # Generate response
            response = self.client.chat_completion(
                messages=messages,
                model=self.model_id,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
            
            # Extract response
            ai_response = response.choices[0].message.content
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"Generated response in {response_time_ms}ms")
            
            return {
                "response": ai_response,
                "model": self.model_id,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "response_time_ms": response_time_ms,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Return a fallback response
            return {
                "response": "I apologize, but I'm having trouble processing that right now. Could you please try again?",
                "model": self.model_id,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "response_time_ms": response_time_ms,
                "success": False,
                "error": str(e)
            }
    
    async def generate_streaming_response(self, context: str, temperature: float = 0.7,
                                        max_tokens: int = 500):
        """
        Generate a streaming response using Mistral 7B
        
        Yields chunks of the response as they are generated
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a caring AI companion with persistent memory, supporting elderly users with empathy and understanding."
                },
                {
                    "role": "user",
                    "content": context
                }
            ]
            
            # Generate streaming response
            stream = self.client.chat_completion(
                messages=messages,
                model=self.model_id,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Failed to generate streaming response: {e}")
            yield f"I apologize, but I'm having trouble responding right now."
    
    def validate_token(self) -> bool:
        """Validate that the HF token has proper access"""
        try:
            # Try a minimal request to validate token
            test_response = self.client.chat_completion(
                messages=[{"role": "user", "content": "Hello"}],
                model=self.model_id,
                max_tokens=10
            )
            return True
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return False


# Global instance
mistral_inference = MistralInference()