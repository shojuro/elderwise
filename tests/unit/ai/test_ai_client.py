import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.ai.base import AIProvider, AIRequest, AIResponse, ProviderConfig
from src.ai.client import AIClient
from src.ai.providers.mock import MockProvider


class TestAIClient:
    """Test suite for AI Client abstraction layer"""
    
    @pytest.fixture
    async def ai_client(self):
        """Create a fresh AI client for testing"""
        client = AIClient()
        yield client
        # Cleanup
        await client.shutdown()
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing"""
        with patch('src.ai.client.settings') as mock_settings:
            mock_settings.ai_provider = "mock"
            mock_settings.ai_fallback_providers = []
            mock_settings.ai_timeout = 60
            mock_settings.ai_max_retries = 3
            mock_settings.hf_token = "test_token"
            mock_settings.cleoai_endpoint = "http://test.com"
            mock_settings.cleoai_api_key = "test_key"
            yield mock_settings
    
    @pytest.mark.asyncio
    async def test_initialize(self, ai_client, mock_settings):
        """Test client initialization"""
        await ai_client.initialize()
        
        assert ai_client._initialized is True
        assert ai_client.primary_provider is not None
        assert isinstance(ai_client.primary_provider, MockProvider)
    
    @pytest.mark.asyncio
    async def test_generate_response(self, ai_client, mock_settings):
        """Test basic response generation"""
        await ai_client.initialize()
        
        response = await ai_client.generate_response(
            context="Hello, how are you?",
            temperature=0.7,
            max_tokens=100,
            user_id="test_user"
        )
        
        assert response.success is True
        assert response.provider == AIProvider.MOCK
        assert len(response.response) > 0
        assert response.response_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_streaming_response(self, ai_client, mock_settings):
        """Test streaming response generation"""
        await ai_client.initialize()
        
        chunks = []
        async for chunk in ai_client.generate_streaming_response(
            context="Tell me a story",
            temperature=0.8,
            max_tokens=50
        ):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert len(full_response) > 0
    
    @pytest.mark.asyncio
    async def test_fallback_behavior(self, ai_client):
        """Test fallback to secondary provider on primary failure"""
        with patch('src.ai.client.settings') as mock_settings:
            mock_settings.ai_provider = "mistral"
            mock_settings.ai_fallback_providers = ["mock"]
            mock_settings.ai_timeout = 60
            mock_settings.hf_token = "invalid_token"
            
            # Initialize with a failing primary provider
            await ai_client.initialize()
            
            # Mock the primary provider to fail
            ai_client.primary_provider.generate_response = AsyncMock(
                side_effect=Exception("Primary provider failed")
            )
            
            # Should fallback to mock provider
            response = await ai_client.generate_response(
                context="Test fallback",
                temperature=0.5
            )
            
            # Response should come from fallback provider
            assert response.response != ""  # Mock provider returns a response
    
    @pytest.mark.asyncio
    async def test_health_check(self, ai_client, mock_settings):
        """Test health check functionality"""
        await ai_client.initialize()
        
        health = await ai_client.health_check()
        
        assert health["initialized"] is True
        assert health["overall_status"] == "healthy"
        assert health["primary_provider"]["status"] == "healthy"
        assert health["primary_provider"]["provider"] == "mock"
    
    @pytest.mark.asyncio
    async def test_provider_caching(self, ai_client, mock_settings):
        """Test that providers are cached and reused"""
        await ai_client.initialize()
        
        # Get provider config
        config = ai_client._get_provider_config("mock")
        
        # Create provider twice
        provider1 = await ai_client._get_or_create_provider(config)
        provider2 = await ai_client._get_or_create_provider(config)
        
        # Should be the same instance
        assert provider1 is provider2
        assert len(ai_client.provider_cache) == 1
    
    @pytest.mark.asyncio
    async def test_invalid_provider_config(self, ai_client):
        """Test handling of invalid provider configuration"""
        with pytest.raises(ValueError, match="Unknown provider"):
            ai_client._get_provider_config("invalid_provider")
    
    @pytest.mark.asyncio
    async def test_all_providers_fail(self, ai_client):
        """Test behavior when all providers fail"""
        with patch('src.ai.client.settings') as mock_settings:
            mock_settings.ai_provider = "mock"
            mock_settings.ai_fallback_providers = []
            
            await ai_client.initialize()
            
            # Make the provider fail
            ai_client.primary_provider.generate_response = AsyncMock(
                side_effect=Exception("Provider failed")
            )
            
            response = await ai_client.generate_response(
                context="Test all fail",
                temperature=0.5
            )
            
            assert response.success is False
            assert "All providers failed" in response.error
            assert "unable to process your request" in response.response
    
    @pytest.mark.asyncio
    async def test_request_metadata_passthrough(self, ai_client, mock_settings):
        """Test that metadata is passed through correctly"""
        await ai_client.initialize()
        
        metadata = {"test_key": "test_value", "number": 42}
        
        response = await ai_client.generate_response(
            context="Test metadata",
            metadata=metadata
        )
        
        assert response.metadata["test_key"] == "test_value"
        assert response.metadata["number"] == 42
        assert response.metadata["mock"] is True  # Added by mock provider
    
    @pytest.mark.asyncio
    async def test_shutdown(self, ai_client, mock_settings):
        """Test proper shutdown and cleanup"""
        await ai_client.initialize()
        
        assert ai_client._initialized is True
        assert len(ai_client.provider_cache) > 0
        
        await ai_client.shutdown()
        
        assert ai_client._initialized is False
        assert len(ai_client.provider_cache) == 0
        assert ai_client.primary_provider is None
        assert len(ai_client.fallback_providers) == 0


@pytest.mark.asyncio
async def test_mistral_provider_integration():
    """Test Mistral provider with mocked HuggingFace client"""
    from src.ai.providers.mistral import MistralProvider
    
    config = ProviderConfig(
        provider=AIProvider.MISTRAL,
        api_key="test_token",
        model_id="mistralai/Mistral-7B-Instruct-v0.3"
    )
    
    provider = MistralProvider(config)
    
    # Mock the HuggingFace client
    with patch('src.ai.providers.mistral.InferenceClient') as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        
        # Mock chat completion response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_response.usage = Mock(
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15
        )
        mock_instance.chat_completion.return_value = mock_response
        
        await provider.initialize()
        
        request = AIRequest(
            context="Test context",
            temperature=0.7,
            max_tokens=100
        )
        
        response = await provider.generate_response(request)
        
        assert response.success is True
        assert response.response == "Test response"
        assert response.provider == AIProvider.MISTRAL
        assert response.usage["total_tokens"] == 15


@pytest.mark.asyncio
async def test_cleoai_provider_integration():
    """Test CleoAI provider with mocked HTTP client"""
    from src.ai.providers.cleoai import CleoAIProvider
    import httpx
    
    config = ProviderConfig(
        provider=AIProvider.CLEOAI,
        endpoint="http://test.cleoai.com",
        api_key="test_key"
    )
    
    provider = CleoAIProvider(config)
    
    # Mock httpx client
    with patch('src.ai.providers.cleoai.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Mock health check
        mock_client.get.return_value = Mock(status_code=200)
        
        # Mock GraphQL response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "inferText": {
                    "text": "CleoAI response",
                    "metadata": {
                        "model": "cleoai-v1",
                        "responseTimeMs": 150,
                        "tokensUsed": 25
                    },
                    "success": True,
                    "error": None
                }
            }
        }
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response
        
        await provider.initialize()
        
        request = AIRequest(
            context="Test CleoAI",
            temperature=0.8,
            max_tokens=200,
            user_id="test_user"
        )
        
        response = await provider.generate_response(request)
        
        assert response.success is True
        assert response.response == "CleoAI response"
        assert response.provider == AIProvider.CLEOAI
        assert response.model == "cleoai-v1"