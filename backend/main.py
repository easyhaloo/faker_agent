"""
Main entry point for the Faker Agent backend.
"""
import logging
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import modules to ensure they are loaded
import backend.modules.weather

from backend.api.routes import router as api_router
from backend.config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Faker Agent API",
    description="API for the Faker Agent intelligent system",
    version=settings.APP_VERSION,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_PREFIX)


# Health check endpoint
@app.get("/")
async def root() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "online", "version": settings.APP_VERSION}


# Startup event
@app.on_event("startup")
async def startup_event():
    """Runs on application startup."""
    logger.info(f"Starting Faker Agent API v{settings.APP_VERSION}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Runs on application shutdown."""
    logger.info("Shutting down Faker Agent API")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)