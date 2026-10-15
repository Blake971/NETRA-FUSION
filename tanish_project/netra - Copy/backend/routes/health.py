from fastapi import APIRouter
from datetime import datetime
from config.settings import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running.
    
    Returns:
        JSON with status, version, and timestamp
    """
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "version": "2.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "environment": settings.environment
        }
    }
