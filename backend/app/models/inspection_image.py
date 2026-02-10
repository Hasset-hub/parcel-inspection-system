"""Inspection Image model"""
from sqlalchemy import Column, String, UUID, ForeignKey, DateTime, Integer, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.session import Base

class InspectionImage(Base):
    __tablename__ = "inspection_images"
    
    image_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    inspection_id = Column(UUID(as_uuid=True), ForeignKey('inspections.inspection_id'), nullable=False)
    
    # Image details
    angle = Column(String(50))  # front, back, left, right, top, bottom
    sequence_number = Column(Integer)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer)
    
    # Image metadata
    width = Column(Integer)
    height = Column(Integer)
    format = Column(String(20))
    
    # AI processing
    processed = Column(Boolean, default=False)
    processing_time_ms = Column(Integer)
    
    # Timestamps
    captured_at = Column(DateTime, default=datetime.utcnow)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    inspection = relationship("Inspection", back_populates="images")
    
    def __repr__(self):
        return f"<InspectionImage {self.angle} for {self.inspection_id}>"
