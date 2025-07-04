from typing import Optional, Dict, Any, AsyncGenerator, List
import logging
import asyncio
from src.ai.base import (
    AIProvider,
    AIProviderInterface,
    AIRequest,
    AIResponse,
    ProviderConfig,
    AIProviderError
)
from src.ai.providers import MistralProvider, CleoAIProvider, MockProvider
from src.config.settings import settings

logger = logging.getLogger(__name__)


class AIClient:
    """
    AI Client Factory with fallback support
    
    This client manages multiple AI providers and can:
    - Switch between providers based on configuration
    - Fallback to secondary providers on failure
    - Cache provider instances
    - Handle provider health checks
    """
    
    # Provider class mapping
    PROVIDERS = {
        AIProvider.MISTRAL: MistralProvider,
        AIProvider.CLEOAI: CleoAIProvider,
        AIProvider.MOCK: MockProvider
    }
    
    def __init__(self):
        self.primary_provider: Optional[AIProviderInterface] = None
        self.fallback_providers: List[AIProviderInterface] = []
        self.provider_cache: Dict[AIProvider, AIProviderInterface] = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the AI client with configured providers"""
        if self._initialized:
            return
        
        try:
            # Load primary provider from settings
            primary_config = self._get_provider_config(settings.ai_provider)
            self.primary_provider = await self._get_or_create_provider(primary_config)
            
            # Load fallback providers if configured
            if hasattr(settings, 'ai_fallback_providers'):
                for provider_name in settings.ai_fallback_providers:
                    try:
                        fallback_config = self._get_provider_config(provider_name)
                        provider = await self._get_or_create_provider(fallback_config)
                        self.fallback_providers.append(provider)
                    except Exception as e:
                        logger.warning(f"Failed to initialize fallback provider {provider_name}: {e}")
            
            self._initialized = True
            logger.info(f"AI Client initialized with primary provider: {settings.ai_provider}")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI client: {e}")
            raise
    
    def _get_provider_config(self, provider_name: str) -> ProviderConfig:
        """Get provider configuration from settings"""
        provider = AIProvider(provider_name)
        
        if provider == AIProvider.MISTRAL:
            return ProviderConfig(
                provider=provider,
                api_key=settings.hf_token,
                model_id=getattr(settings, 'mistral_model_id', "mistralai/Mistral-7B-Instruct-v0.3"),
                timeout=getattr(settings, 'ai_timeout', 60)
            )
        
        elif provider == AIProvider.CLEOAI:
            return ProviderConfig(
                provider=provider,
                endpoint=getattr(settings, 'cleoai_endpoint', "http://localhost:8000"),
                api_key=getattr(settings, 'cleoai_api_key', None),
                timeout=getattr(settings, 'ai_timeout', 60),
                max_retries=getattr(settings, 'ai_max_retries', 3)
            )
        
        elif provider == AIProvider.MOCK:
            return ProviderConfig(
                provider=provider,
                timeout=1
            )
        
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
    
    async def _get_or_create_provider(self, config: ProviderConfig) -> AIProviderInterface:
        """Get provider from cache or create new instance"""
        if config.provider in self.provider_cache:
            return self.provider_cache[config.provider]
        
        provider_class = self.PROVIDERS.get(config.provider)
        if not provider_class:
            raise ValueError(f"No implementation for provider: {config.provider}")
        
        provider = provider_class(config)
        await provider.initialize()
        
        self.provider_cache[config.provider] = provider
        return provider
    
    async def generate_response(
        self,
        context: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> AIResponse:
        """
        Generate AI response with automatic fallback
        
        Args:
            context: The full context string for the AI
            temperature: Control randomness (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            user_id: Optional user identifier
            session_id: Optional session identifier
            metadata: Optional metadata to pass through
            stream: Whether to use streaming (returns AsyncGenerator if True)
            
        Returns:
            AIResponse object or AsyncGenerator for streaming
        """
        if not self._initialized:
            await self.initialize()
        
        request = AIRequest(
            context=context,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata
        )
        
        # Try primary provider first
        providers_to_try = [self.primary_provider] + self.fallback_providers
        last_error = None
        
        for provider in providers_to_try:
            try:
                logger.info(f"Attempting response generation with {provider.config.provider.value}")
                
                if stream:
                    # For streaming, we return the generator directly
                    # The caller will need to handle potential failures
                    return provider.generate_streaming_response(request)
                else:
                    response = await provider.generate_response(request)
                    
                    if response.success:
                        return response
                    else:
                        logger.warning(f"Provider {provider.config.provider.value} returned unsuccessful response: {response.error}")
                        last_error = response.error
                        
            except Exception as e:
                logger.error(f"Provider {provider.config.provider.value} failed: {e}")
                last_error = str(e)
                continue
        
        # All providers failed
        logger.error(f"All AI providers failed. Last error: {last_error}")
        
        # Return error response
        return AIResponse(
            response="I apologize, but I'm unable to process your request at this time. Please try again later.",
            provider=AIProvider.MISTRAL,  # Default to primary provider type
            model="unknown",
            temperature=temperature,
            max_tokens=max_tokens,
            response_time_ms=0,
            success=False,
            error=f"All providers failed. Last error: {last_error}"
        )
    
    async def generate_streaming_response(
        self,
        context: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming AI response
        
        This is a convenience method that calls generate_response with stream=True
        """
        result = await self.generate_response(
            context=context,
            temperature=temperature,
            max_tokens=max_tokens,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata,
            stream=True
        )
        
        # Result should be an AsyncGenerator
        if hasattr(result, '__aiter__'):
            async for chunk in result:
                yield chunk
        else:
            # Fallback if something went wrong
            yield "I apologize, but streaming is not available at this time."
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all configured providers"""
        if not self._initialized:
            await self.initialize()
        
        health_status = {
            "initialized": self._initialized,
            "primary_provider": None,
            "fallback_providers": [],
            "overall_status": "unhealthy"
        }
        
        # Check primary provider
        if self.primary_provider:
            health_status["primary_provider"] = await self.primary_provider.health_check()
            if health_status["primary_provider"]["status"] == "healthy":
                health_status["overall_status"] = "healthy"
        
        # Check fallback providers
        for provider in self.fallback_providers:
            provider_health = await provider.health_check()
            health_status["fallback_providers"].append(provider_health)
            if provider_health["status"] == "healthy" and health_status["overall_status"] == "unhealthy":
                health_status["overall_status"] = "degraded"
        
        return health_status
    
    async def shutdown(self) -> None:
        """Shutdown all providers and cleanup resources"""
        for provider in self.provider_cache.values():
            try:
                await provider.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down provider {provider.config.provider.value}: {e}")
        
        self.provider_cache.clear()
        self.primary_provider = None
        self.fallback_providers.clear()
        self._initialized = False
        logger.info("AI Client shut down")


# Global AI client instance
ai_client = AIClient()