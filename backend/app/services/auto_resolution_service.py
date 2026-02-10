"""Auto-resolution service for automatic parcel decisions"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Optional
from uuid import UUID
from datetime import datetime

from app.models.parcel import Parcel
from app.models.inspection import Inspection
from app.models.system_setting import SystemSetting

class AutoResolutionService:
    """Service for automatic parcel resolution decisions"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = {}
    
    async def load_settings(self):
        """Load auto-resolution settings from database"""
        result = await self.db.execute(
            select(SystemSetting).where(
                SystemSetting.category == 'auto_resolution',
                SystemSetting.is_active == True
            )
        )
        settings = result.scalars().all()
        
        for setting in settings:
            if setting.value_type == 'number':
                self.settings[setting.setting_key] = float(setting.setting_value)
            elif setting.value_type == 'boolean':
                self.settings[setting.setting_key] = setting.setting_value.lower() == 'true'
            else:
                self.settings[setting.setting_key] = setting.setting_value
    
    def get_setting(self, key: str, default=None):
        """Get setting value with fallback"""
        return self.settings.get(key, default)
    
    async def evaluate_parcel(
        self,
        parcel_id: UUID,
        inspection_id: UUID
    ) -> Dict:
        """
        Evaluate parcel and make auto-resolution decision
        
        Returns:
            Decision dict with action, confidence, and reasoning
        """
        # Load settings
        await self.load_settings()
        
        # Get parcel and inspection
        parcel_result = await self.db.execute(
            select(Parcel).where(Parcel.parcel_id == parcel_id)
        )
        parcel = parcel_result.scalar_one()
        
        inspection_result = await self.db.execute(
            select(Inspection).where(Inspection.inspection_id == inspection_id)
        )
        inspection = inspection_result.scalar_one()
        
        # Check if auto-resolution is enabled
        if not self.get_setting('auto_approve_enabled', True):
            return {
                'can_auto_resolve': False,
                'action': 'manual_review',
                'reason': 'Auto-resolution disabled',
                'confidence': 0.0
            }
        
        # Check minimum images
        min_images = self.get_setting('min_images_for_auto_resolution', 6)
        if inspection.images_received < min_images:
            return {
                'can_auto_resolve': False,
                'action': 'manual_review',
                'reason': f'Insufficient images ({inspection.images_received}/{min_images})',
                'confidence': 0.0
            }
        
        # Get thresholds
        approve_confidence = self.get_setting('auto_approve_confidence_threshold', 0.95)
        quarantine_confidence = self.get_setting('auto_quarantine_confidence_threshold', 0.70)
        max_damage_for_approve = self.get_setting('auto_approve_max_damage_score', 0.10)
        min_damage_for_quarantine = self.get_setting('auto_quarantine_min_damage_score', 0.30)
        
        # Calculate damage score from inspection
        damage_score = 0.0
        if inspection.has_damage:
            # Simple calculation: damage_count / images * average_confidence
            if inspection.damage_count > 0:
                damage_score = min(1.0, inspection.damage_count / inspection.images_received)
        
        # Decision logic
        decision = self._make_decision(
            inspection=inspection,
            damage_score=damage_score,
            approve_confidence=approve_confidence,
            quarantine_confidence=quarantine_confidence,
            max_damage_for_approve=max_damage_for_approve,
            min_damage_for_quarantine=min_damage_for_quarantine
        )
        
        return decision
    
    def _make_decision(
        self,
        inspection: Inspection,
        damage_score: float,
        approve_confidence: float,
        quarantine_confidence: float,
        max_damage_for_approve: float,
        min_damage_for_quarantine: float
    ) -> Dict:
        """Make resolution decision based on rules"""
        
        # Rule 1: No damage detected with high confidence → APPROVE
        if not inspection.has_damage and inspection.overall_confidence >= approve_confidence:
            return {
                'can_auto_resolve': True,
                'action': 'approved',
                'reason': 'No damage detected with high confidence',
                'confidence': inspection.overall_confidence,
                'damage_score': damage_score,
                'rule_triggered': 'no_damage_high_confidence'
            }
        
        # Rule 2: Minor damage with low score → APPROVE
        if damage_score <= max_damage_for_approve:
            return {
                'can_auto_resolve': True,
                'action': 'approved',
                'reason': 'Damage score below threshold for approval',
                'confidence': inspection.overall_confidence,
                'damage_score': damage_score,
                'rule_triggered': 'minor_damage_acceptable'
            }
        
        # Rule 3: Significant damage detected → QUARANTINE
        if damage_score >= min_damage_for_quarantine and inspection.overall_confidence >= quarantine_confidence:
            return {
                'can_auto_resolve': True,
                'action': 'quarantine',
                'reason': 'Significant damage detected',
                'confidence': inspection.overall_confidence,
                'damage_score': damage_score,
                'rule_triggered': 'damage_detected'
            }
        
        # Rule 4: Low confidence → MANUAL REVIEW
        if inspection.overall_confidence < quarantine_confidence:
            return {
                'can_auto_resolve': False,
                'action': 'manual_review',
                'reason': 'Low detection confidence',
                'confidence': inspection.overall_confidence,
                'damage_score': damage_score,
                'rule_triggered': 'low_confidence'
            }
        
        # Default: Manual review for edge cases
        return {
            'can_auto_resolve': False,
            'action': 'manual_review',
            'reason': 'Edge case - requires human judgment',
            'confidence': inspection.overall_confidence,
            'damage_score': damage_score,
            'rule_triggered': 'edge_case'
        }
    
    async def apply_decision(
        self,
        parcel_id: UUID,
        decision: Dict
    ):
        """Apply auto-resolution decision to parcel"""
        
        result = await self.db.execute(
            select(Parcel).where(Parcel.parcel_id == parcel_id)
        )
        parcel = result.scalar_one()
        
        if decision['can_auto_resolve']:
            parcel.auto_resolved = True
            parcel.resolution_action = decision['action']
            parcel.status = decision['action']
            parcel.completed_at = datetime.utcnow()
        else:
            parcel.auto_resolved = False
            parcel.resolution_action = None
            parcel.status = 'manual_review'
        
        await self.db.commit()
        await self.db.refresh(parcel)
        
        return parcel
