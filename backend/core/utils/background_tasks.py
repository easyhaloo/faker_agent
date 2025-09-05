"""
Background tasks for the Faker Agent.

This module provides utilities for running background tasks such as
cleaning up expired memories.
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from backend.core.infrastructure.database import db_session
from backend.core.models.database_models import MemoryProfileDB, MemoryEpisodeDB

# Configure logger
logger = logging.getLogger(__name__)


class BackgroundTaskManager:
    """Manager for background tasks."""
    
    def __init__(self):
        self.running = False
        self.task: Optional[asyncio.Task] = None
    
    async def start_cleanup_task(self, interval: int = 3600):
        """
        Start the cleanup task that runs periodically.
        
        Args:
            interval: Interval in seconds between cleanup runs (default: 1 hour)
        """
        if self.running:
            logger.warning("Cleanup task is already running")
            return
            
        self.running = True
        self.task = asyncio.create_task(self._cleanup_loop(interval))
        logger.info(f"Started cleanup task with interval {interval}s")
    
    async def stop_cleanup_task(self):
        """Stop the cleanup task."""
        if not self.running:
            logger.warning("Cleanup task is not running")
            return
            
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped cleanup task")
    
    async def _cleanup_loop(self, interval: int):
        """
        Main cleanup loop.
        
        Args:
            interval: Interval in seconds between cleanup runs
        """
        while self.running:
            try:
                await self.cleanup_expired_memories()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                # Continue running even if one iteration fails
                await asyncio.sleep(interval)
    
    async def cleanup_expired_memories(self):
        """Clean up expired memories from the database."""
        logger.info("Starting cleanup of expired memories")
        
        current_time = datetime.now()
        cleaned_count = 0
        
        # Clean up expired profile memories
        with db_session() as db:
            try:
                expired_profiles = db.query(MemoryProfileDB).filter(
                    MemoryProfileDB.expires_at.isnot(None),
                    MemoryProfileDB.expires_at < current_time
                ).all()
                
                for profile in expired_profiles:
                    db.delete(profile)
                    cleaned_count += 1
                    
                db.commit()
                logger.info(f"Cleaned up {len(expired_profiles)} expired profile memories")
            except Exception as e:
                logger.error(f"Error cleaning up profile memories: {e}")
                db.rollback()
        
        # Clean up expired episode memories
        with db_session() as db:
            try:
                expired_episodes = db.query(MemoryEpisodeDB).filter(
                    MemoryEpisodeDB.expires_at.isnot(None),
                    MemoryEpisodeDB.expires_at < current_time
                ).all()
                
                for episode in expired_episodes:
                    db.delete(episode)
                    cleaned_count += 1
                    
                db.commit()
                logger.info(f"Cleaned up {len(expired_episodes)} expired episode memories")
            except Exception as e:
                logger.error(f"Error cleaning up episode memories: {e}")
                db.rollback()
        
        logger.info(f"Completed cleanup of expired memories. Removed {cleaned_count} items")


# Global instance
background_task_manager = BackgroundTaskManager()