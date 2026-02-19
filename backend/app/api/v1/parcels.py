"""Parcel management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from uuid import UUID

from app.db.session import get_db
from app.models.parcel import Parcel
from app.models.inspection import Inspection
from app.models.damage_detection import DamageDetection

router = APIRouter()


@router.get("/")
async def get_parcels(
    status: Optional[str] = None,
    has_damage: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get list of parcels with filtering"""
    query = select(Parcel)
    
    if status:
        query = query.where(Parcel.status == status)
    if has_damage is not None:
        query = query.where(Parcel.has_damage == has_damage)
    if search:
        query = query.where(Parcel.tracking_number.ilike(f"%{search}%"))
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Parcel.created_at.desc())
    
    result = await db.execute(query)
    parcels = result.scalars().all()
    
    return {
        "parcels": [
            {
                "parcel_id": str(p.parcel_id),
                "tracking_number": p.tracking_number,
                "status": p.status,
                "has_damage": p.has_damage,
                "damage_severity": p.damage_severity,
                "auto_resolved": p.auto_resolved,
                "resolution_reason": p.auto_resolution_reason,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in parcels
        ],
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }


@router.get("/{parcel_id}")
async def get_parcel_by_id(
    parcel_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed parcel information including inspections"""
    result = await db.execute(
        select(Parcel).where(Parcel.parcel_id == parcel_id)
    )
    parcel = result.scalar_one_or_none()
    
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")
    
    # Get inspections
    inspections_result = await db.execute(
        select(Inspection)
        .where(Inspection.parcel_id == parcel_id)
        .order_by(Inspection.started_at.desc())
    )
    inspections = inspections_result.scalars().all()
    
    # Get damage count for each inspection
    inspection_list = []
    for inspection in inspections:
        damage_count_result = await db.execute(
            select(func.count(DamageDetection.detection_id))
            .where(DamageDetection.inspection_id == inspection.inspection_id)
        )
        damage_count = damage_count_result.scalar() or 0
        
        inspection_list.append({
            "inspection_id": str(inspection.inspection_id),
            "inspection_type": inspection.inspection_type,
            "overall_status": inspection.overall_status,
            "damage_count": damage_count,
            "created_at": inspection.started_at.isoformat() if inspection.started_at else None,
            "completed_at": inspection.completed_at.isoformat() if inspection.completed_at else None,
        })
    
    return {
        "parcel_id": str(parcel.parcel_id),
        "tracking_number": parcel.tracking_number,
        "status": parcel.status,
        "has_damage": parcel.has_damage,
        "damage_severity": parcel.damage_severity,
        "damage_value_estimate": float(parcel.damage_value_estimate) if parcel.damage_value_estimate else None,
        "auto_resolved": parcel.auto_resolved,
        "auto_resolution_reason": parcel.auto_resolution_reason,
        "current_location": parcel.current_location,
        "weight_kg": float(parcel.weight_kg) if parcel.weight_kg else None,
        "created_at": parcel.created_at.isoformat() if parcel.created_at else None,
        "updated_at": parcel.updated_at.isoformat() if parcel.updated_at else None,
        "received_at": parcel.received_at.isoformat() if parcel.received_at else None,
        "inspected_at": parcel.inspected_at.isoformat() if parcel.inspected_at else None,
        "inspections": inspection_list
    }


@router.patch("/{parcel_id}/status")
async def update_parcel_status(
    parcel_id: UUID,
    status: str,
    db: AsyncSession = Depends(get_db)
):
    """Update parcel status"""
    result = await db.execute(
        select(Parcel).where(Parcel.parcel_id == parcel_id)
    )
    parcel = result.scalar_one_or_none()
    
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")
    
    valid_statuses = ['received', 'inspecting', 'approved', 'damaged', 'quarantine', 'stored', 'picked', 'shipped', 'returned']
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    parcel.status = status
    await db.commit()
    await db.refresh(parcel)
    
    return {
        "parcel_id": str(parcel.parcel_id),
        "tracking_number": parcel.tracking_number,
        "status": parcel.status,
        "updated_at": parcel.updated_at.isoformat() if parcel.updated_at else None,
    }


@router.post("/bulk-update")
async def bulk_update_status(
    parcel_ids: List[UUID],
    status: str,
    db: AsyncSession = Depends(get_db)
):
    """Bulk update parcel statuses"""
    valid_statuses = ['received', 'inspecting', 'approved', 'damaged', 'quarantine', 'stored', 'picked', 'shipped', 'returned']
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    result = await db.execute(
        select(Parcel).where(Parcel.parcel_id.in_(parcel_ids))
    )
    parcels = result.scalars().all()
    
    if not parcels:
        raise HTTPException(status_code=404, detail="No parcels found")
    
    for parcel in parcels:
        parcel.status = status
    
    await db.commit()
    
    return {
        "updated_count": len(parcels),
        "status": status,
        "parcel_ids": [str(p.parcel_id) for p in parcels]
    }
