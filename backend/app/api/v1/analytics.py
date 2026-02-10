"""Analytics endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get dashboard statistics
    
    Returns overall system metrics
    """
    stats = await AnalyticsService.get_dashboard_stats(db)
    return stats

@router.get("/supplier/{supplier_id}/scorecard")
async def get_supplier_scorecard(
    supplier_id: UUID,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """
    Get supplier performance scorecard
    
    - **supplier_id**: UUID of supplier
    - **days**: Number of days to analyze (default: 30)
    """
    scorecard = await AnalyticsService.get_supplier_scorecard(
        db=db,
        supplier_id=supplier_id,
        days=days
    )
    return scorecard
