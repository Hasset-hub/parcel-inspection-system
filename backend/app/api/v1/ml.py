"""ML endpoints for damage detection"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid
from app.services.ml_service import get_damage_detection_service
from app.core.config import settings

router = APIRouter()

@router.post("/detect-damage")
async def detect_damage(
    file: UploadFile = File(...)
):
    """
    Analyze image for damage using YOLO
    
    - **file**: Image file to analyze
    
    Returns damage analysis with detections
    """
    # Save uploaded file temporarily
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_ext = file.filename.split('.')[-1].lower()
    temp_filename = f"temp_{uuid.uuid4()}.{file_ext}"
    temp_path = upload_dir / temp_filename
    
    # Save file
    contents = await file.read()
    with open(temp_path, "wb") as f:
        f.write(contents)
    
    try:
        # Get ML service
        ml_service = get_damage_detection_service()
        
        # Analyze for damage
        result = ml_service.analyze_damage(str(temp_path))
        
        return {
            'filename': file.filename,
            'has_damage': result['has_damage'],
            'damage_score': result['damage_score'],
            'damage_type': result['damage_type'],
            'detections': result['detections'],
            'detection_count': result['detection_count']
        }
    
    finally:
        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()

@router.get("/model-info")
async def get_model_info():
    """Get information about the ML model"""
    ml_service = get_damage_detection_service()
    return ml_service.get_model_info()
