from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, Any
import logging
from src.utils.database import mongodb_manager, redis_manager, pinecone_manager
from src.utils.scheduler import memory_scheduler
from src.api.routes import ai_router, user_router, memory_router
from src.config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting ElderWise AI application...")
    
    # Connect to databases
    try:
        redis_manager.connect()
        await mongodb_manager.connect()
        pinecone_manager.connect()
        logger.info("All database connections established")
        
        # Start scheduler
        memory_scheduler.start()
        logger.info("Memory scheduler started")
    except Exception as e:
        logger.error(f"Failed to connect to databases: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down ElderWise AI application...")
    memory_scheduler.stop()
    redis_manager.disconnect()
    await mongodb_manager.disconnect()
    logger.info("All database connections closed")


# Create FastAPI app
app = FastAPI(
    title="ElderWise AI",
    description="Memory-driven AI companion for elderly care",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ai_router, prefix="/ai", tags=["AI"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(memory_router, prefix="/memory", tags=["Memory"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ElderWise AI API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "services": {
            "redis": "unknown",
            "mongodb": "unknown",
            "pinecone": "unknown"
        }
    }
    
    # Check Redis
    try:
        redis_manager.get_client().ping()
        health_status["services"]["redis"] = "connected"
    except:
        health_status["services"]["redis"] = "disconnected"
        health_status["status"] = "degraded"
    
    # Check MongoDB
    try:
        await mongodb_manager.client.admin.command('ping')
        health_status["services"]["mongodb"] = "connected"
    except:
        health_status["services"]["mongodb"] = "disconnected"
        health_status["status"] = "degraded"
    
    # Check Pinecone
    try:
        pinecone_manager.get_index().describe_index_stats()
        health_status["services"]["pinecone"] = "connected"
    except:
        health_status["services"]["pinecone"] = "disconnected"
        health_status["status"] = "degraded"
    
    return health_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )