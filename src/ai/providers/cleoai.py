from typing import AsyncGenerator, Dict, Any, Optional
import httpx
import json
import time
import asyncio
import logging
from src.ai.base import (
    AIProviderInterface,
    AIRequest,
    AIResponse,
    AIProvider,
    ProviderConfig,
    AIProviderConnectionError,
    AIProviderAuthenticationError,
    AIProviderResponseError,
    AIProviderRateLimitError
)

logger = logging.getLogger(__name__)


class CleoAIProvider(AIProviderInterface):
    """CleoAI provider using GraphQL/REST API"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client: Optional[httpx.AsyncClient] = None
        self.endpoint = config.endpoint or "http://localhost:8000"
        self.graphql_endpoint = f"{self.endpoint}/graphql"
        self.rest_endpoint = f"{self.endpoint}/api"
        self.api_key = config.api_key
        self.headers = {
            "Content-Type": "application/json",
            **(config.custom_headers or {})
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    async def initialize(self) -> None:
        """Initialize the HTTP client and validate connection"""
        try:
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.timeout),
                headers=self.headers,
                limits=httpx.Limits(max_keepalive_connections=10)
            )
            
            # Validate the connection
            if await self.validate_connection():
                self._initialized = True
                logger.info(f"Initialized CleoAI provider at {self.endpoint}")
            else:
                raise AIProviderConnectionError("Failed to validate CleoAI connection")
                
        except Exception as e:
            logger.error(f"Failed to initialize CleoAI provider: {e}")
            raise AIProviderConnectionError(f"Failed to initialize: {str(e)}")
    
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generate a response using CleoAI GraphQL API"""
        if not self._initialized:
            await self.initialize()
        
        start_time = time.time()
        
        # GraphQL mutation for inference
        mutation = """
        mutation InferText($input: InferenceInput!) {
            inferText(input: $input) {
                text
                metadata {
                    model
                    temperature
                    maxTokens
                    tokensUsed
                    responseTimeMs
                }
                error
                success
            }
        }
        """
        
        variables = {
            "input": {
                "text": request.context,
                "temperature": request.temperature,
                "maxTokens": request.max_tokens,
                "userId": request.user_id,
                "sessionId": request.session_id,
                "stream": False,
                "metadata": request.metadata
            }
        }
        
        try:
            # Retry logic for resilience
            for attempt in range(self.config.max_retries):
                try:
                    response = await self.client.post(
                        self.graphql_endpoint,
                        json={
                            "query": mutation,
                            "variables": variables
                        }
                    )
                    
                    if response.status_code == 429:  # Rate limited
                        retry_after = int(response.headers.get("Retry-After", self.config.retry_delay))
                        if attempt < self.config.max_retries - 1:
                            await asyncio.sleep(retry_after)
                            continue
                        else:
                            raise AIProviderRateLimitError("Rate limited by CleoAI")
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    if "errors" in data:
                        raise AIProviderResponseError(f"GraphQL errors: {data['errors']}")
                    
                    result = data["data"]["inferText"]
                    
                    if not result["success"]:
                        raise AIProviderResponseError(f"CleoAI error: {result.get('error', 'Unknown error')}")
                    
                    # Calculate total response time
                    response_time_ms = int((time.time() - start_time) * 1000)
                    
                    # Extract usage information
                    usage = None
                    if result["metadata"].get("tokensUsed"):
                        usage = {
                            "total_tokens": result["metadata"]["tokensUsed"],
                            "model": result["metadata"].get("model", "cleoai")
                        }
                    
                    return AIResponse(
                        response=result["text"],
                        provider=AIProvider.CLEOAI,
                        model=result["metadata"].get("model", "cleoai"),
                        temperature=request.temperature,
                        max_tokens=request.max_tokens,
                        response_time_ms=response_time_ms,
                        success=True,
                        usage=usage,
                        metadata={
                            **(request.metadata or {}),
                            "cleoai_response_time": result["metadata"].get("responseTimeMs")
                        }
                    )
                    
                except httpx.HTTPStatusError as e:
                    if e.response.status_code != 429:  # Not rate limit
                        raise
                    
            # If we get here, all retries failed
            raise AIProviderRateLimitError("Exceeded maximum retries for CleoAI")
            
        except Exception as e:
            logger.error(f"Failed to generate CleoAI response: {e}")
            response_time_ms = int((time.time() - start_time) * 1000)
            
            return AIResponse(
                response="I apologize, but I'm having trouble connecting to my AI service. Please try again.",
                provider=AIProvider.CLEOAI,
                model="cleoai",
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                response_time_ms=response_time_ms,
                success=False,
                error=str(e)
            )
    
    async def generate_streaming_response(
        self, request: AIRequest
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response using CleoAI SSE endpoint"""
        if not self._initialized:
            await self.initialize()
        
        # Use REST endpoint for streaming
        stream_endpoint = f"{self.rest_endpoint}/infer/stream"
        
        try:
            async with self.client.stream(
                "POST",
                stream_endpoint,
                json={
                    "text": request.context,
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                    "user_id": request.user_id,
                    "session_id": request.session_id,
                    "metadata": request.metadata
                }
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        
                        if data == "[DONE]":
                            break
                        
                        try:
                            chunk = json.loads(data)
                            if "text" in chunk:
                                yield chunk["text"]
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse SSE chunk: {data}")
                            
        except Exception as e:
            logger.error(f"Failed to generate streaming response: {e}")
            yield "I apologize, but I'm having trouble streaming the response right now."
    
    async def validate_connection(self) -> bool:
        """Validate connection to CleoAI service"""
        try:
            if not self.client:
                return False
            
            # Use health endpoint
            response = await self.client.get(f"{self.endpoint}/health")
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"CleoAI connection validation failed: {e}")
            return False
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about CleoAI model capabilities"""
        try:
            query = """
            query GetModelInfo {
                modelInfo {
                    name
                    version
                    capabilities
                    contextLength
                    supportedLanguages
                }
            }
            """
            
            response = await self.client.post(
                self.graphql_endpoint,
                json={"query": query}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data and "modelInfo" in data["data"]:
                    return data["data"]["modelInfo"]
            
        except Exception as e:
            logger.warning(f"Failed to get CleoAI model info: {e}")
        
        # Return default info if query fails
        return {
            "name": "CleoAI",
            "version": "unknown",
            "capabilities": ["chat", "streaming", "memory", "moe"],
            "context_length": 32768,
            "provider": "CleoAI Service"
        }
    
    async def shutdown(self) -> None:
        """Clean up HTTP client"""
        if self.client:
            await self.client.aclose()
            self.client = None
            self._initialized = False