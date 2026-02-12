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

    @staticmethod
    async def get_damage_trends(
        db: AsyncSession,
        days: int = 30
    ) -> List[Dict]:
        """Get damage counts grouped by day"""
        since_date = datetime.utcnow() - timedelta(days=days)

        result = await db.execute(
            select(
                func.date(Inspection.completed_at).label('date'),
                func.count(Inspection.inspection_id).label('count')
            )
            .where(Inspection.completed_at >= since_date)
            .group_by(func.date(Inspection.completed_at))
            .order_by(func.date(Inspection.completed_at))
        )
        rows = result.all()

        # Fill in missing days with 0
        date_map = {str(row.date): row.count for row in rows}
        trend_data = []
        for i in range(days):
            day = (datetime.utcnow() - timedelta(days=days - i)).strftime('%Y-%m-%d')
            trend_data.append({
                'date': day,
                'count': date_map.get(day, 0),
                'severity_avg': 0.0
            })

        return trend_data

    @staticmethod
    async def get_damage_by_type(
        db: AsyncSession
    ) -> List[Dict]:
        """Get damage counts grouped by type"""
        from app.models.damage_detection import DamageDetection

        result = await db.execute(
            select(
                DamageDetection.damage_type,
                func.count(DamageDetection.detection_id).label('count')
            )
            .group_by(DamageDetection.damage_type)
            .order_by(func.count(DamageDetection.detection_id).desc())
        )
        rows = result.all()

        total = sum(row.count for row in rows) or 1

        return [
            {
                'damage_type': row.damage_type or 'unknown',
                'count': row.count,
                'percentage': round(row.count / total * 100, 1)
            }
            for row in rows
        ]

    @staticmethod
    async def get_supplier_performance(
        db: AsyncSession,
        limit: int = 10
    ) -> List[Dict]:
        """Get top suppliers by damage rate"""
        result = await db.execute(
            select(Supplier)
            .where(Supplier.is_active == True)
            .order_by(Supplier.damage_rate.desc())
            .limit(limit)
        )
        suppliers = result.scalars().all()

        return [
            {
                'supplier_name': s.name,
                'supplier_code': s.supplier_code,
                'total_parcels': s.total_shipments or 0,
                'damaged_parcels': s.total_damaged_parcels or 0,
                'damage_rate': float(s.damage_rate or 0)
            }
            for s in suppliers
        ]
