from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    
    # Redis
    REDIS_URL: str
    REDIS_CACHE_TTL: int = 300
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    API_RELOAD: bool = True
    API_DEBUG: bool = True
    
    # Storage
    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_PATH: str = "/tmp/parcel_images"
    
    # ML
    ML_MODEL_PATH: str = "../ml/models/yolov8n.pt"
    OCR_ENABLED: bool = True
    OCR_LANGUAGE: str = "en"
    GPU_ENABLED: bool = False
    
    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "../logs/app.log"
    
    # CORS
    # include common dev origins (Vite default 5173 and CRA 3000)
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # Image Upload Settings
    UPLOAD_DIR: str = "/tmp/parcel-images"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,webp"
    IMAGES_PER_INSPECTION: int = 6
    
    @property
    def allowed_extensions_list(self) -> list[str]:
        return self.ALLOWED_EXTENSIONS.split(',')
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png,image/jpg"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create singleton instance
settings = Settings()

    
