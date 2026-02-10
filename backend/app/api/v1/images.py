"""Image upload endpoints"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import os
import uuid
from pathlib import Path
from PIL import Image
from app.core.config import settings

router = APIRouter()

def validate_image(file: UploadFile) -> None:
    """Validate uploaded image"""
    # Check extension
    ext = file.filename.split('.')[-1].lower()
    if ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Check file size (approximate)
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(0)  # Reset
    
    if size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE} bytes"
        )

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...)
):
    """
    Upload a single image
    
    - **file**: Image file (JPG, PNG, WEBP)
    """
    # Validate
    validate_image(file)
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_ext = file.filename.split('.')[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = upload_dir / unique_filename
    
    # Save file
    contents = await file.read()
    
    # Verify it's a valid image
    try:
        img = Image.open(io.BytesIO(contents))
        img.verify()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    # Save to disk
    with open(file_path, "wb") as f:
        f.write(contents)
    
    return {
        "filename": unique_filename,
        "path": str(file_path),
        "size": len(contents),
        "content_type": file.content_type
    }

@router.post("/upload-multiple")
async def upload_multiple_images(
    files: List[UploadFile] = File(...)
):
    """
    Upload multiple images (multi-angle inspection)
    
    - **files**: List of image files (max 6)
    """
    if len(files) > settings.IMAGES_PER_INSPECTION:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Max: {settings.IMAGES_PER_INSPECTION}"
        )
    
    uploaded_files = []
    
    for file in files:
        # Validate
        validate_image(file)
        
        # Create upload directory
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_ext = file.filename.split('.')[-1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = upload_dir / unique_filename
        
        # Save file
        contents = await file.read()
        
        # Verify valid image
        try:
            img = Image.open(io.BytesIO(contents))
            img.verify()
            width, height = img.size
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid image: {file.filename}")
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        uploaded_files.append({
            "filename": unique_filename,
            "original_name": file.filename,
            "path": str(file_path),
            "size": len(contents),
            "dimensions": {"width": width, "height": height}
        })
    
    return {
        "count": len(uploaded_files),
        "files": uploaded_files
    }

import io
