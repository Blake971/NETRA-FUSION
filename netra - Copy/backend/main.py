from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from routes.health import router as health_router
from routes.scan import router as scan_router
from routes.history import router as history_router
from routes.tools import router as tools_router
from database.database import init_db
from models.scan import Scan

# Initialize FastAPI app
app = FastAPI(
    title="NETRA API",
    description="AI-Powered Digital Footprint & Security Assessment Platform",
    version="2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health_router, tags=["Health"])
app.include_router(scan_router, tags=["Scan"])
app.include_router(history_router, tags=["History"])
app.include_router(tools_router, tags=["Tools"])

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "NETRA API v2.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
