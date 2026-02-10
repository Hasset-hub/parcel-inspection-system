"""Inspection model"""
from sqlalchemy import Column, String, UUID, ForeignKey, DateTime, Boolean, Float, Text, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.session import Base

class Inspection(Base):
    __tablename__ = "inspections"
    
    inspection_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    parcel_id = Column(UUID(as_uuid=True), ForeignKey('parcels.parcel_id'), nullable=False)
    inspector_user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    
    # Inspection details
    inspection_type = Column(String(50), default='automated')  # automated, manual, appeal
    overall_status = Column(String(50), default='in_progress')  # in_progress, completed, failed
    overall_confidence = Column(Float)
    
    # Damage assessment
    has_damage = Column(Boolean, default=False)
    damage_count = Column(Integer, default=0)
    damage_types = Column(JSONB)  # List of detected damage types
    
    # AI/ML results
    ml_model_version = Column(String(50))
    ml_results = Column(JSONB)  # Store raw ML output
    
    # Multi-angle details
    images_expected = Column(Integer, default=6)
    images_received = Column(Integer, default=0)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parcel = relationship("Parcel", back_populates="inspections")
    images = relationship("InspectionImage", back_populates="inspection", cascade="all, delete-orphan")
    detections = relationship("DamageDetection", back_populates="inspection", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Inspection {self.inspection_id} for Parcel {self.parcel_id}>"
