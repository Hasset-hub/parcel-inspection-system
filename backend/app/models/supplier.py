"""Supplier model"""
from sqlalchemy import Column, String, UUID, Float, Integer, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import uuid
from app.db.session import Base

class Supplier(Base):
    __tablename__ = "suppliers"
    
    supplier_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    
    # Contact
    contact_email = Column(String(200))
    contact_phone = Column(String(50))
    address = Column(Text)
    
    # Performance metrics
    damage_rate = Column(Float, default=0.0)
    total_parcels_received = Column(Integer, default=0)
    damaged_parcels_count = Column(Integer, default=0)
    
    # SLA metrics
    on_time_delivery_rate = Column(Float, default=1.0)
    late_deliveries = Column(Integer, default=0)
    
    # Ratings
    quality_rating = Column(Float, default=5.0)  # 1-5 scale
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Supplier {self.supplier_code}: {self.name}>"

from sqlalchemy import Boolean
