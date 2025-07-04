import redis
from motor.motor_asyncio import AsyncIOMotorClient
from pinecone import Pinecone, ServerlessSpec
from typing import Optional
import logging
from src.config.settings import settings

logger = logging.getLogger(__name__)


class RedisManager:
    def __init__(self):
        self.client: Optional[redis.Redis] = None
    
    def connect(self):
        try:
            self.client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=True
            )
            self.client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def disconnect(self):
        if self.client:
            self.client.close()
            logger.info("Redis connection closed")
    
    def get_client(self) -> redis.Redis:
        if not self.client:
            self.connect()
        return self.client


class MongoDBManager:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
    
    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(settings.mongodb_uri)
            self.db = self.client[settings.mongodb_database]
            await self.client.admin.command('ping')
            logger.info("MongoDB connection established")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def get_db(self):
        if not self.db:
            raise RuntimeError("MongoDB not connected")
        return self.db
    
    def get_collection(self, name: str):
        return self.get_db()[name]


class PineconeManager:
    def __init__(self):
        self.pc: Optional[Pinecone] = None
        self.index = None
    
    def connect(self):
        try:
            self.pc = Pinecone(api_key=settings.pinecone_api_key)
            
            # Create index if it doesn't exist
            if settings.pinecone_index_name not in self.pc.list_indexes().names():
                self.pc.create_index(
                    name=settings.pinecone_index_name,
                    dimension=384,  # For sentence-transformers/all-MiniLM-L6-v2
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region=settings.pinecone_environment
                    )
                )
                logger.info(f"Created Pinecone index: {settings.pinecone_index_name}")
            
            self.index = self.pc.Index(settings.pinecone_index_name)
            logger.info("Pinecone connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Pinecone: {e}")
            raise
    
    def get_index(self):
        if not self.index:
            self.connect()
        return self.index


# Global instances
redis_manager = RedisManager()
mongodb_manager = MongoDBManager()
pinecone_manager = PineconeManager()