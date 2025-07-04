from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import logging
from src.memory.storage import MemoryStorage
from src.memory.semantic import SemanticMemory
from src.config.settings import settings

logger = logging.getLogger(__name__)


class MemoryScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.storage = MemoryStorage()
        self.semantic = SemanticMemory()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """Configure scheduled jobs"""
        
        # Daily memory archival job - runs at 2 AM
        self.scheduler.add_job(
            self.archive_memories,
            CronTrigger(hour=2, minute=0),
            id="memory_archival",
            name="Archive old memories",
            misfire_grace_time=3600  # 1 hour grace period
        )
        
        # Weekly cleanup job - runs on Sundays at 3 AM
        self.scheduler.add_job(
            self.cleanup_expired_memories,
            CronTrigger(day_of_week=0, hour=3, minute=0),
            id="memory_cleanup",
            name="Clean up expired memories",
            misfire_grace_time=7200  # 2 hour grace period
        )
        
        # Hourly stats logging - for monitoring
        self.scheduler.add_job(
            self.log_memory_stats,
            CronTrigger(minute=0),  # Every hour on the hour
            id="stats_logging",
            name="Log memory statistics"
        )
        
        logger.info("Scheduled jobs configured")
    
    async def archive_memories(self):
        """Archive memories older than active period"""
        try:
            logger.info("Starting memory archival job")
            
            # Archive in MongoDB
            archived_count = await self.storage.archive_old_memories()
            
            # TODO: Update vectors in Pinecone with archive status
            # This would require fetching all vectors and updating their metadata
            
            logger.info(f"Memory archival completed. Archived {archived_count} memories")
            
        except Exception as e:
            logger.error(f"Error in memory archival job: {e}")
    
    async def cleanup_expired_memories(self):
        """Remove memories older than retention period"""
        try:
            logger.info("Starting memory cleanup job")
            
            # Calculate cutoff date
            cutoff_days = settings.memory_archive_days
            cutoff_date = datetime.utcnow() - timedelta(days=cutoff_days)
            
            # Find and remove expired memories from MongoDB
            collection = self.storage.db.get_collection("memory_fragments")
            result = await collection.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            deleted_count = result.deleted_count
            
            logger.info(f"Memory cleanup completed. Removed {deleted_count} expired memories")
            
        except Exception as e:
            logger.error(f"Error in memory cleanup job: {e}")
    
    async def log_memory_stats(self):
        """Log system-wide memory statistics"""
        try:
            # Get counts from MongoDB
            db = self.storage.db.get_db()
            
            stats = {
                "users": await db.user_profiles.count_documents({}),
                "active_memories": await db.memory_fragments.count_documents({"retention": "active"}),
                "archived_memories": await db.memory_fragments.count_documents({"retention": "archive"}),
                "total_interactions": await db.interaction_logs.count_documents({})
            }
            
            logger.info(f"Memory system stats: {stats}")
            
        except Exception as e:
            logger.error(f"Error logging memory stats: {e}")
    
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Memory scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Memory scheduler stopped")
    
    def get_jobs(self):
        """Get list of scheduled jobs"""
        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            }
            for job in self.scheduler.get_jobs()
        ]


# Global scheduler instance
memory_scheduler = MemoryScheduler()