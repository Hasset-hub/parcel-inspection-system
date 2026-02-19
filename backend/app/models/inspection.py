"""Inspection model"""
from sqlalchemy import Column, String, ForeignKey, Boolean, Numeric, Integer, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.session import Base


class Inspection(Base):
    __tablename__ = "inspections"
    
    inspection_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parcel_id = Column(UUID(as_uuid=True), ForeignKey('parcels.parcel_id', ondelete='CASCADE'))
    inspector_user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    device_id = Column(String(100))
    
    # Inspection details
    inspection_type = Column(String(50), default='receiving')
    overall_status = Column(String(20))
    overall_confidence = Column(Numeric(5, 4))
    
    # OCR and labels
    ocr_text = Column(Text)
    labels_detected = Column(ARRAY(Text))
    hazard_warnings = Column(ARRAY(Text))
    missing_labels = Column(ARRAY(Text))
    
    # Verification
    expected_appearance_match_score = Column(Numeric(5, 4))
    tampering_detected = Column(Boolean, default=False)
    wrong_packaging_detected = Column(Boolean, default=False)
    
    # Notes
    notes = Column(Text)
    
    # Timestamps
    started_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    completed_at = Column(TIMESTAMP(timezone=True))
    duration_seconds = Column(Integer)
    
    # Relationships
    parcel = relationship("Parcel", back_populates="inspections")
    images = relationship("InspectionImage", back_populates="inspection", cascade="all, delete-orphan")
    damage_detections = relationship("DamageDetection", back_populates="inspection", cascade="all, delete-orphan")
    
    # Computed property for damage_count
    @property
    def damage_count(self):
        """Get count of damage detections"""
        if hasattr(self, 'damage_detections') and self.damage_detections:
            return len(self.damage_detections)
        return 0
    
    @property
    def created_at(self):
        """Alias for started_at"""
        return self.started_at
    
    def __repr__(self):
        return f"<Inspection {self.inspection_id}>"
