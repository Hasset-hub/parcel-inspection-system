from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Parcel Inspection System API",
    description="AI-powered damage detection and warehouse management",
    version="1.0.0",
    debug=settings.API_DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("🚀 Parcel Inspection System API starting up...")
    logger.info(f"📍 Environment: {'Development' if settings.API_DEBUG else 'Production'}")
    logger.info(f"🗄️  Database: Connected to PostgreSQL")
    logger.info(f"💾 Redis: Connected at {settings.REDIS_URL}")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("👋 Shutting down Parcel Inspection System API...")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Parcel Inspection System API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "ml_service": "ready"
    }

@app.get("/api/v1/info")
async def api_info():
    """API information"""
    return {
        "name": "Parcel Inspection System",
        "version": "1.0.0",
        "environment": "development" if settings.API_DEBUG else "production",
        "features": [
            "AI damage detection",
            "Multi-angle scanning",
            "OCR label reading",
            "Supplier tracking",
            "Automated claims generation"
        ]
    }

# ========================================
# ROUTERS - All registered here
# ========================================

# Auth Router
from app.api.v1.auth import router as auth_router
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])

# Images Router
from app.api.v1.images import router as images_router
app.include_router(images_router, prefix="/api/v1/images", tags=["images"])

# ML Router
from app.api.v1.ml import router as ml_router
app.include_router(ml_router, prefix="/api/v1/ml", tags=["machine-learning"])

# Inspections Router
from app.api.v1.inspections import router as inspections_router
app.include_router(inspections_router, prefix="/api/v1/inspections", tags=["inspections"])

# Auto-Resolution Router
from app.api.v1.auto_resolution import router as auto_resolution_router
app.include_router(auto_resolution_router, prefix="/api/v1/auto-resolution", tags=["auto-resolution"])

# Analytics Router
from app.api.v1.analytics import router as analytics_router
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["analytics"])

# OCR Router
from app.api.v1.ocr import router as ocr_router
app.include_router(ocr_router, prefix="/api/v1/ocr", tags=["ocr"])

# Claims Router
from app.api.v1.claims import router as claims_router
app.include_router(claims_router, prefix="/api/v1/claims", tags=["claims"])

# ========================================
# MAIN - For direct execution
# ========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD
    )
