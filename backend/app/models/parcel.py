"""Parcel model"""
from sqlalchemy import Column, String, UUID, ForeignKey, DateTime, Boolean, Float, Text, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.session import Base

class Parcel(Base):
    __tablename__ = "parcels"
    
    parcel_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tracking_number = Column(String(100), unique=True, nullable=False, index=True)
    
    # Foreign keys
    shipment_id = Column(UUID(as_uuid=True), ForeignKey('shipments.shipment_id'))
    sku_id = Column(UUID(as_uuid=True), ForeignKey('skus.sku_id'))
    current_warehouse_id = Column(UUID(as_uuid=True), ForeignKey('warehouses.warehouse_id'))
    
    # Status and dimensions
    status = Column(String(50), default='received', index=True)
    weight_kg = Column(Float)
    length_cm = Column(Float)
    width_cm = Column(Float)
    height_cm = Column(Float)
    
    # Damage flags
    has_damage = Column(Boolean, default=False, index=True)
    damage_severity = Column(String(20))  # minor, moderate, severe
    damage_description = Column(Text)
    
    # Auto-resolution
    auto_resolved = Column(Boolean, default=False)
    resolution_action = Column(String(50))  # approved, quarantine, rejected
    
    # Metadata
    metadata_json = Column(JSONB)
    notes = Column(Text)
    
    # Timestamps
    received_at = Column(DateTime, default=datetime.utcnow)
    inspected_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    inspections = relationship("Inspection", back_populates="parcel")
    
    def __repr__(self):
        return f"<Parcel {self.tracking_number}>"
