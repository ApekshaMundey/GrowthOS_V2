import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.core.exceptions import setup_exception_handlers

app = FastAPI(
    title="GrowthOS API",
    description="Backend API for GrowthOS platform",
    version="1.0.0",
)

# Set up global exception handling
setup_exception_handlers(app)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """Minimal health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": int(time.time()),
        "environment": settings.ENV
    }

from app.api.router import api_router

app.include_router(api_router)
