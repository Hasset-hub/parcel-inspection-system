"""Analytics service for supplier performance and metrics"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, List
from uuid import UUID
from datetime import datetime, timedelta

from app.models.supplier import Supplier
from app.models.parcel import Parcel
from app.models.inspection import Inspection

class AnalyticsService:
    """Service for analytics and reporting"""
    
    @staticmethod
    async def get_supplier_scorecard(
        db: AsyncSession,
        supplier_id: UUID,
        days: int = 30
    ) -> Dict:
        """
        Get comprehensive supplier scorecard
        
        Args:
            supplier_id: UUID of supplier
            days: Number of days to analyze
        """
        # Get supplier
        supplier_result = await db.execute(
            select(Supplier).where(Supplier.supplier_id == supplier_id)
        )
        supplier = supplier_result.scalar_one_or_none()
        
        if not supplier:
            return {"error": "Supplier not found"}
        
        # Date range
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Get parcels from this supplier in date range
        # (Assuming parcels link to supplier via shipment)
        # For now, using all supplier parcels
        
        scorecard = {
            'supplier_id': str(supplier.supplier_id),
            'supplier_code': supplier.supplier_code,
            'supplier_name': supplier.name,
            'period_days': days,
            'metrics': {
                'damage_rate': supplier.damage_rate,
                'total_parcels': supplier.total_parcels_received,
                'damaged_parcels': supplier.damaged_parcels_count,
                'on_time_delivery_rate': supplier.on_time_delivery_rate,
                'quality_rating': supplier.quality_rating,
            },
            'status': 'active' if supplier.is_active else 'inactive',
            'generated_at': datetime.utcnow()
        }
        
        return scorecard
    
    @staticmethod
    async def get_dashboard_stats(
        db: AsyncSession
    ) -> Dict:
        """Get dashboard statistics"""
        
        # Total parcels
        total_parcels_result = await db.execute(
            select(func.count(Parcel.parcel_id))
        )
        total_parcels = total_parcels_result.scalar()
        
        # Parcels with damage
        damaged_parcels_result = await db.execute(
            select(func.count(Parcel.parcel_id)).where(Parcel.has_damage == True)
        )
        damaged_parcels = damaged_parcels_result.scalar()
        
        # Auto-resolved parcels
        auto_resolved_result = await db.execute(
            select(func.count(Parcel.parcel_id)).where(Parcel.auto_resolved == True)
        )
        auto_resolved = auto_resolved_result.scalar()
        
        # Completed inspections
        completed_inspections_result = await db.execute(
            select(func.count(Inspection.inspection_id)).where(
                Inspection.overall_status == 'completed'
            )
        )
        completed_inspections = completed_inspections_result.scalar()
        
        # Calculate rates
        damage_rate = (damaged_parcels / total_parcels * 100) if total_parcels > 0 else 0
        auto_resolution_rate = (auto_resolved / total_parcels * 100) if total_parcels > 0 else 0
        
        return {
            'total_parcels': total_parcels,
            'damaged_parcels': damaged_parcels,
            'auto_resolved': auto_resolved,
            'completed_inspections': completed_inspections,
            'damage_rate': round(damage_rate, 2),
            'auto_resolution_rate': round(auto_resolution_rate, 2),
            'generated_at': datetime.utcnow()
        }
