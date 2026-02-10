"""Parcel schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class ParcelBase(BaseModel):
    tracking_number: str
    weight_kg: Optional[float] = None
    length_cm: Optional[float] = None
    width_cm: Optional[float] = None
    height_cm: Optional[float] = None

class ParcelCreate(ParcelBase):
    shipment_id: Optional[UUID] = None
    sku_id: Optional[UUID] = None
    current_warehouse_id: Optional[UUID] = None

class ParcelUpdate(BaseModel):
    status: Optional[str] = None
    has_damage: Optional[bool] = None
    damage_severity: Optional[str] = None
    damage_description: Optional[str] = None
    notes: Optional[str] = None

class ParcelResponse(ParcelBase):
    parcel_id: UUID
    status: str
    has_damage: bool
    damage_severity: Optional[str]
    auto_resolved: bool
    resolution_action: Optional[str]
    received_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True
