"""
Main application entry point for the Faker Agent backend.

This module initializes the FastAPI application, sets up middleware,
configures routes, and starts background tasks.
"""
import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.main_router import router
from backend.config.settings import settings
from backend.core.infrastructure.database import engine, Base
from backend.core.utils.background_tasks import background_task_manager
from backend.core.utils.logging import setup_logging

# Configure logging
setup_logging()

# Configure logger
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events including database initialization
    and background task management.
    """
    # Startup
    logger.info("Starting Faker Agent backend")
    
    # Create database tables
    logger.info("Creating database tables")
    Base.metadata.create_all(bind=engine)
    
    # Start background tasks
    logger.info("Starting background tasks")
    await background_task_manager.start_cleanup_task(settings.MEMORY_CLEANUP_INTERVAL)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Faker Agent backend")
    
    # Stop background tasks
    logger.info("Stopping background tasks")
    await background_task_manager.stop_cleanup_task()


# Create FastAPI app with lifespan manager
app = FastAPI(
    title="Faker Agent API",
    description="API for the Faker Agent multi-session conversation system",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"message": "Faker Agent backend is running"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )