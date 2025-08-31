"""
Database initialization module.

This module provides functions to initialize the database and create tables.
"""
import logging

from backend.core.infrastructure.database import engine, Base
from backend.core.models.database_models import (
    ConversationDB,
    MessageDB,
    MemoryProfileDB,
    MemoryEpisodeDB,
    ConversationSummaryDB,
    MemoryAuditDB,
    MemorySettingsDB
)

# Configure logger
logger = logging.getLogger(__name__)


def initialize_database():
    """
    Initialize the database by creating all tables.
    """
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


if __name__ == "__main__":
    # Run this directly to initialize the database
    initialize_database()