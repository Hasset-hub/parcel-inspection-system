"""OCR endpoints"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid
from app.services.ocr_service import get_ocr_service
from app.core.config import settings

router = APIRouter()

@router.post("/extract-text")
async def extract_text_from_image(
    file: UploadFile = File(...)
):
    """
    Extract text from image using OCR
    
    - **file**: Image file to process
    
    Returns extracted text with confidence
    """
    # Save file temporarily
    upload_dir = Path(settings.UPLOAD_DIR) / "ocr"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_ext = file.filename.split('.')[-1].lower()
    temp_filename = f"ocr_{uuid.uuid4()}.{file_ext}"
    temp_path = upload_dir / temp_filename
    
    # Save file
    contents = await file.read()
    with open(temp_path, "wb") as f:
        f.write(contents)
    
    try:
        # Extract text
        ocr_service = get_ocr_service()
        result = ocr_service.extract_text(str(temp_path))
        
        return {
            'filename': file.filename,
            'success': result['success'],
            'text': result.get('text', ''),
            'confidence': result.get('confidence', 0.0),
            'word_count': result.get('word_count', 0),
            'error': result.get('error')
        }
    
    finally:
        # Clean up
        if temp_path.exists():
            temp_path.unlink()

@router.post("/extract-label")
async def extract_shipping_label(
    file: UploadFile = File(...)
):
    """
    Extract shipping label information
    
    - **file**: Shipping label image
    
    Returns tracking number, carrier, dimensions, weight
    """
    # Save file temporarily
    upload_dir = Path(settings.UPLOAD_DIR) / "ocr"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_ext = file.filename.split('.')[-1].lower()
    temp_filename = f"label_{uuid.uuid4()}.{file_ext}"
    temp_path = upload_dir / temp_filename
    
    contents = await file.read()
    with open(temp_path, "wb") as f:
        f.write(contents)
    
    try:
        ocr_service = get_ocr_service()
        label_info = ocr_service.extract_label_info(str(temp_path))
        
        return label_info
    
    finally:
        if temp_path.exists():
            temp_path.unlink()

@router.post("/extract-tracking")
async def extract_tracking_number(
    text: str
):
    """
    Extract tracking number from text
    
    - **text**: Text containing tracking number
    
    Returns tracking number and carrier
    """
    ocr_service = get_ocr_service()
    tracking_info = ocr_service.extract_tracking_number(text)
    
    if tracking_info:
        return tracking_info
    else:
        return {
            'success': False,
            'message': 'No tracking number found'
        }
