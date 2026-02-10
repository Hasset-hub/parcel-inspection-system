"""Inspection endpoints"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import uuid
from pathlib import Path
from PIL import Image as PILImage

from app.db.session import get_db
from app.schemas.inspection import (
    InspectionCreate,
    InspectionResponse,
    InspectionUpdate
)
from app.services.inspection_service import InspectionService
from app.core.config import settings

router = APIRouter()

@router.post("/", response_model=InspectionResponse)
async def create_inspection(
    inspection_data: InspectionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create new inspection for a parcel
    
    - **parcel_id**: UUID of parcel to inspect
    - **inspection_type**: Type of inspection (automated, manual)
    """
    inspection = await InspectionService.create_inspection(
        db=db,
        parcel_id=inspection_data.parcel_id,
        inspection_type=inspection_data.inspection_type
    )
    
    return inspection

@router.post("/{inspection_id}/upload-image")
async def upload_inspection_image(
    inspection_id: UUID,
    angle: str,
    sequence_number: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload image for inspection
    
    - **inspection_id**: UUID of inspection
    - **angle**: Image angle (front, back, left, right, top, bottom)
    - **sequence_number**: Order of image (1-6)
    - **file**: Image file
    """
    # Save file
    upload_dir = Path(settings.UPLOAD_DIR) / "inspections" / str(inspection_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_ext = file.filename.split('.')[-1].lower()
    filename = f"{angle}_{sequence_number}.{file_ext}"
    file_path = upload_dir / filename
    
    # Save and get dimensions
    contents = await file.read()
    
    # Verify and get image info
    try:
        img = PILImage.open(io.BytesIO(contents))
        width, height = img.size
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Add to database
    inspection_image = await InspectionService.add_inspection_image(
        db=db,
        inspection_id=inspection_id,
        file_path=str(file_path),
        angle=angle,
        sequence_number=sequence_number,
        width=width,
        height=height,
        file_size=len(contents)
    )
    
    # Process with ML
    detections = await InspectionService.process_image_with_ml(
        db=db,
        image_id=inspection_image.image_id
    )
    
    return {
        "image_id": inspection_image.image_id,
        "file_path": str(file_path),
        "processed": True,
        "detections_found": len(detections)
    }

@router.post("/{inspection_id}/complete", response_model=InspectionResponse)
async def complete_inspection(
    inspection_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Complete inspection and finalize results
    
    - **inspection_id**: UUID of inspection to complete
    """
    inspection = await InspectionService.complete_inspection(
        db=db,
        inspection_id=inspection_id
    )
    
    return inspection

@router.get("/{inspection_id}", response_model=InspectionResponse)
async def get_inspection(
    inspection_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get inspection details"""
    from sqlalchemy import select
    from app.models.inspection import Inspection
    
    result = await db.execute(
        select(Inspection).where(Inspection.inspection_id == inspection_id)
    )
    inspection = result.scalar_one_or_none()
    
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    return inspection

import io
