from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    # Hugging Face
    hf_token: str
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017/"
    mongodb_database: str = "elderwise_ai"
    
    # Pinecone
    pinecone_api_key: str
    pinecone_environment: str = "us-west1-gcp"
    pinecone_index_name: str = "elderwise-memory"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    
    # Memory Settings
    memory_active_days: int = 90
    memory_archive_days: int = 365
    memory_context_limit: int = 10
    
    # AI Provider Settings
    ai_provider: str = "mistral"  # Options: mistral, cleoai, mock
    ai_fallback_providers: List[str] = []  # e.g., ["mock"] or ["cleoai", "mock"]
    ai_timeout: int = 60  # seconds
    ai_max_retries: int = 3
    
    # Mistral Specific Settings
    mistral_model_id: str = "mistralai/Mistral-7B-Instruct-v0.3"
    
    # CleoAI Specific Settings
    cleoai_endpoint: Optional[str] = "http://localhost:8000"
    cleoai_api_key: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()