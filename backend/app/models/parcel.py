"""Parcel model"""
from sqlalchemy import Column, String, ForeignKey, Boolean, Numeric, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
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
    packaging_type_id = Column(UUID(as_uuid=True), ForeignKey('packaging_types.packaging_type_id'))
    current_warehouse_id = Column(UUID(as_uuid=True), ForeignKey('warehouses.warehouse_id'))
    
    # Dimensions
    weight_kg = Column(Numeric(10, 3))
    length_cm = Column(Numeric(8, 2))
    width_cm = Column(Numeric(8, 2))
    height_cm = Column(Numeric(8, 2))
    dimension_mismatch = Column(Boolean, default=False)
    weight_mismatch = Column(Boolean, default=False)
    
    # Location
    current_location = Column(String(200))
    
    # Status
    status = Column(String(50), default='received', index=True)
    
    # Damage
    has_damage = Column(Boolean, default=False, index=True)
    damage_severity = Column(String(20))  # minor, moderate, severe, total_loss
    damage_value_estimate = Column(Numeric(12, 2))
    
    # Auto-resolution
    auto_resolved = Column(Boolean, default=False)
    auto_resolution_reason = Column(Text)
    
    # Tags
    tags = Column(ARRAY(Text))
    
    # Timestamps
    received_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    inspected_at = Column(TIMESTAMP(timezone=True))
    stored_at = Column(TIMESTAMP(timezone=True))
    shipped_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    inspections = relationship("Inspection", back_populates="parcel", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Parcel {self.tracking_number}>"
