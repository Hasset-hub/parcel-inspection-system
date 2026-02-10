"""Auto-resolution endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Dict

from app.db.session import get_db
from app.services.auto_resolution_service import AutoResolutionService

router = APIRouter()

@router.post("/evaluate/{parcel_id}/{inspection_id}")
async def evaluate_parcel_for_auto_resolution(
    parcel_id: UUID,
    inspection_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Evaluate parcel for auto-resolution
    
    - **parcel_id**: UUID of parcel
    - **inspection_id**: UUID of completed inspection
    
    Returns decision with action and reasoning
    """
    service = AutoResolutionService(db)
    decision = await service.evaluate_parcel(parcel_id, inspection_id)
    
    return decision

@router.post("/apply/{parcel_id}")
async def apply_auto_resolution(
    parcel_id: UUID,
    decision: Dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Apply auto-resolution decision to parcel
    
    - **parcel_id**: UUID of parcel
    - **decision**: Decision dict from evaluation
    """
    service = AutoResolutionService(db)
    parcel = await service.apply_decision(parcel_id, decision)
    
    return {
        "parcel_id": parcel.parcel_id,
        "status": parcel.status,
        "auto_resolved": parcel.auto_resolved,
        "resolution_action": parcel.resolution_action
    }

@router.get("/settings")
async def get_auto_resolution_settings(
    db: AsyncSession = Depends(get_db)
):
    """Get current auto-resolution settings"""
    from sqlalchemy import select
    from app.models.system_setting import SystemSetting
    
    result = await db.execute(
        select(SystemSetting).where(
            SystemSetting.category == 'auto_resolution'
        )
    )
    settings = result.scalars().all()
    
    return {
        setting.setting_key: {
            'value': setting.setting_value,
            'type': setting.value_type,
            'description': setting.description,
            'json_value': setting.json_value
        }
        for setting in settings
    }
