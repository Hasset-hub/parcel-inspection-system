from sqlalchemy import Column, String, Boolean, Numeric, Integer, Date, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.session import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    contact_name = Column(String(200))
    email = Column(String(255))
    phone = Column(String(20))
    address = Column(Text)
    country = Column(String(100))
    total_shipments = Column(Integer, default=0)
    total_damaged_parcels = Column(Integer, default=0)
    damage_rate = Column(Numeric(5, 4), default=0.0)
    avg_packaging_quality_score = Column(Numeric(3, 2))
    contract_start_date = Column(Date)
    contract_end_date = Column(Date)
    sla_delivery_time_hours = Column(Integer)
    sla_damage_threshold = Column(Numeric(5, 4))
    is_active = Column(Boolean, default=True)
