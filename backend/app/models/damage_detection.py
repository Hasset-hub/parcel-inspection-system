"""Damage Detection model"""
from sqlalchemy import Column, String, UUID, ForeignKey, DateTime, Float, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.session import Base

class DamageDetection(Base):
    __tablename__ = "damage_detections"
    
    detection_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    inspection_id = Column(UUID(as_uuid=True), ForeignKey('inspections.inspection_id'), nullable=False)
    image_id = Column(UUID(as_uuid=True), ForeignKey('inspection_images.image_id'))
    
    # Detection details
    damage_type = Column(String(100))  # torn, crushed, dented, etc.
    confidence = Column(Float)
    severity = Column(String(20))  # minor, moderate, severe
    
    # Bounding box (if applicable)
    bbox_x1 = Column(Float)
    bbox_y1 = Column(Float)
    bbox_x2 = Column(Float)
    bbox_y2 = Column(Float)
    
    # ML details
    model_name = Column(String(100))
    model_version = Column(String(50))
    detection_metadata = Column(JSONB)
    
    # Description
    description = Column(Text)
    
    # Timestamps
    detected_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    inspection = relationship("Inspection", back_populates="detections")
    
    def __repr__(self):
        return f"<DamageDetection {self.damage_type} ({self.confidence:.2%})>"
