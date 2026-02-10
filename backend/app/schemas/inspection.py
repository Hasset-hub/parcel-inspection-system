"""Inspection schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class InspectionCreate(BaseModel):
    parcel_id: UUID
    inspection_type: str = "automated"
    images_expected: int = 6

class InspectionImageUpload(BaseModel):
    angle: str  # front, back, left, right, top, bottom
    sequence_number: int

class InspectionUpdate(BaseModel):
    overall_status: Optional[str] = None
    has_damage: Optional[bool] = None
    damage_count: Optional[int] = None
    overall_confidence: Optional[float] = None

class DamageDetectionResponse(BaseModel):
    detection_id: UUID
    damage_type: str
    confidence: float
    severity: Optional[str]
    bbox_x1: Optional[float]
    bbox_y1: Optional[float]
    bbox_x2: Optional[float]
    bbox_y2: Optional[float]
    
    class Config:
        from_attributes = True

class InspectionImageResponse(BaseModel):
    image_id: UUID
    angle: str
    sequence_number: int
    file_path: str
    processed: bool
    width: Optional[int]
    height: Optional[int]
    
    class Config:
        from_attributes = True

class InspectionResponse(BaseModel):
    inspection_id: UUID
    parcel_id: UUID
    inspection_type: str
    overall_status: str
    has_damage: bool
    damage_count: int
    overall_confidence: Optional[float]
    images_expected: int
    images_received: int
    started_at: datetime
    completed_at: Optional[datetime]
    images: List[InspectionImageResponse] = []
    detections: List[DamageDetectionResponse] = []
    
    class Config:
        from_attributes = True
