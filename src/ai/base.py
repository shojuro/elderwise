from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncGenerator, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AIProvider(str, Enum):
    """Supported AI providers"""
    MISTRAL = "mistral"
    CLEOAI = "cleoai"
    MOCK = "mock"  # For testing


@dataclass
class AIRequest:
    """Standardized AI request format"""
    context: str
    temperature: float = 0.7
    max_tokens: int = 500
    stream: bool = False
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AIResponse:
    """Standardized AI response format"""
    response: str
    provider: AIProvider
    model: str
    temperature: float
    max_tokens: int
    response_time_ms: int
    success: bool
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    usage: Optional[Dict[str, int]] = None  # tokens used, etc.


@dataclass
class ProviderConfig:
    """Configuration for an AI provider"""
    provider: AIProvider
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    model_id: Optional[str] = None
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0
    custom_headers: Optional[Dict[str, str]] = None
    additional_config: Optional[Dict[str, Any]] = None


class AIProviderInterface(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider (connect, validate credentials, etc.)"""
        pass
    
    @abstractmethod
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generate a response for the given request"""
        pass
    
    @abstractmethod
    async def generate_streaming_response(
        self, request: AIRequest
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response for the given request"""
        pass
    
    @abstractmethod
    async def validate_connection(self) -> bool:
        """Validate that the provider is properly configured and accessible"""
        pass
    
    @abstractmethod
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        pass
    
    async def shutdown(self) -> None:
        """Clean up any resources (connections, etc.)"""
        pass
    
    def is_initialized(self) -> bool:
        """Check if the provider has been initialized"""
        return self._initialized
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the provider"""
        try:
            is_valid = await self.validate_connection()
            model_info = await self.get_model_info() if is_valid else {}
            
            return {
                "provider": self.config.provider.value,
                "status": "healthy" if is_valid else "unhealthy",
                "initialized": self._initialized,
                "model_info": model_info,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "provider": self.config.provider.value,
                "status": "error",
                "error": str(e),
                "initialized": self._initialized,
                "timestamp": datetime.utcnow().isoformat()
            }


class AIProviderError(Exception):
    """Base exception for AI provider errors"""
    pass


class AIProviderConnectionError(AIProviderError):
    """Raised when unable to connect to the AI provider"""
    pass


class AIProviderAuthenticationError(AIProviderError):
    """Raised when authentication fails"""
    pass


class AIProviderRateLimitError(AIProviderError):
    """Raised when rate limited by the provider"""
    pass


class AIProviderResponseError(AIProviderError):
    """Raised when the provider returns an invalid response"""
    pass