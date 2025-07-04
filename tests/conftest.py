"""
Pytest configuration and shared fixtures for ElderWise tests
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing"""
    client = MagicMock()
    client.ping = MagicMock(return_value=True)
    client.rpush = MagicMock()
    client.lrange = MagicMock(return_value=[])
    client.ltrim = MagicMock()
    client.expire = MagicMock()
    client.delete = MagicMock()
    return client


@pytest.fixture
def mock_mongodb_collection():
    """Mock MongoDB collection for testing"""
    collection = MagicMock()
    collection.insert_one = AsyncMock()
    collection.find_one = AsyncMock()
    collection.update_one = AsyncMock()
    collection.update_many = AsyncMock()
    collection.count_documents = AsyncMock()
    collection.delete_one = AsyncMock()
    
    # Mock cursor
    cursor = MagicMock()
    cursor.sort = MagicMock(return_value=cursor)
    cursor.limit = MagicMock(return_value=cursor)
    cursor.__aiter__ = AsyncMock(return_value=[])
    collection.find = MagicMock(return_value=cursor)
    
    return collection


@pytest.fixture
def mock_pinecone_index():
    """Mock Pinecone index for testing"""
    index = MagicMock()
    index.upsert = MagicMock()
    index.query = MagicMock()
    index.fetch = MagicMock()
    index.delete = MagicMock()
    return index


@pytest.fixture
def sample_user_profile():
    """Sample user profile for testing"""
    from src.models.memory import UserProfile
    return UserProfile(
        user_id="test_user_123",
        name="Test User",
        age=75,
        conditions=["hypertension", "diabetes"],
        interests=["gardening", "reading", "cooking"]
    )


@pytest.fixture
def sample_memory_fragment():
    """Sample memory fragment for testing"""
    from src.models.memory import MemoryFragment
    from datetime import datetime
    return MemoryFragment(
        user_id="test_user_123",
        timestamp=datetime.utcnow(),
        type="health",
        content="User mentioned taking medication this morning",
        tags=["medication", "health", "morning"],
        retention="active"
    )


@pytest.fixture
def sample_interaction_log():
    """Sample interaction log for testing"""
    from src.models.memory import InteractionLog
    from datetime import datetime
    return InteractionLog(
        user_id="test_user_123",
        timestamp=datetime.utcnow(),
        user_message="I took my medication this morning",
        ai_response="That's great! It's important to maintain your medication schedule.",
        response_time_ms=150,
        context_size=1024,
        error=None
    )


@pytest.fixture
def sample_medication_data():
    """Sample medication data for testing"""
    return {
        "medication_id": "198440",
        "name": "Acetaminophen 500 mg",
        "generic_name": "acetaminophen",
        "brand_names": ["Tylenol"],
        "shape": "oval",
        "color": "white",
        "imprint": "L484",
        "dosage_forms": ["tablet"],
        "strength": "500 mg",
        "manufacturer": "Kroger Company"
    }


@pytest.fixture
def sample_pill_features():
    """Sample pill features for testing"""
    from src.services.vision import PillFeatures
    return PillFeatures(
        shape="oval",
        color="white",
        imprint="L484",
        size_estimate="medium",
        confidence=0.85
    )


@pytest.fixture(autouse=True)
def mock_medication_env_vars(monkeypatch):
    """Set up test environment variables for medication services"""
    # Don't set Google Vision API key so tests use mock by default
    monkeypatch.setenv("RXIMAGE_BASE_URL", "http://rximage.nlm.nih.gov/api/rximage/1")
    monkeypatch.setenv("RXNORM_BASE_URL", "https://rxnav.nlm.nih.gov/REST")
    monkeypatch.setenv("FDA_API_BASE_URL", "https://api.fda.gov/drug")