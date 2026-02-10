"""Inspection service for managing parcel inspections"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Optional
from uuid import UUID
import uuid
from datetime import datetime
from pathlib import Path

from app.models.inspection import Inspection
from app.models.inspection_image import InspectionImage
from app.models.damage_detection import DamageDetection
from app.models.parcel import Parcel
from app.services.ml_service import get_damage_detection_service

class InspectionService:
    """Service for managing inspections"""
    
    @staticmethod
    async def create_inspection(
        db: AsyncSession,
        parcel_id: UUID,
        inspector_user_id: Optional[UUID] = None,
        inspection_type: str = "automated"
    ) -> Inspection:
        """Create new inspection for a parcel"""
        
        inspection = Inspection(
            parcel_id=parcel_id,
            inspector_user_id=inspector_user_id,
            inspection_type=inspection_type,
            overall_status="in_progress",
            images_expected=6,
            images_received=0,
            ml_model_version="YOLOv8n"
        )
        
        db.add(inspection)
        await db.commit()
        await db.refresh(inspection)
        
        return inspection
    
    @staticmethod
    async def add_inspection_image(
        db: AsyncSession,
        inspection_id: UUID,
        file_path: str,
        angle: str,
        sequence_number: int,
        width: int,
        height: int,
        file_size: int
    ) -> InspectionImage:
        """Add image to inspection"""
        
        image = InspectionImage(
            inspection_id=inspection_id,
            angle=angle,
            sequence_number=sequence_number,
            file_path=file_path,
            file_size_bytes=file_size,
            width=width,
            height=height,
            format="JPEG",
            processed=False
        )
        
        db.add(image)
        
        # Update inspection images_received count
        result = await db.execute(
            select(Inspection).where(Inspection.inspection_id == inspection_id)
        )
        inspection = result.scalar_one()
        inspection.images_received += 1
        
        await db.commit()
        await db.refresh(image)
        
        return image
    
    @staticmethod
    async def process_image_with_ml(
        db: AsyncSession,
        image_id: UUID
    ) -> List[DamageDetection]:
        """Process image with ML model and create damage detections"""
        
        # Get image
        result = await db.execute(
            select(InspectionImage).where(InspectionImage.image_id == image_id)
        )
        image = result.scalar_one()
        
        # Run ML detection
        ml_service = get_damage_detection_service()
        ml_result = ml_service.analyze_damage(image.file_path)
        
        # Create damage detections
        detections = []
        
        for detection_data in ml_result.get('detections', []):
            detection = DamageDetection(
                inspection_id=image.inspection_id,
                image_id=image_id,
                damage_type=detection_data.get('class_name', 'unknown'),
                confidence=detection_data.get('confidence', 0.0),
                severity="moderate",  # Default
                bbox_x1=detection_data.get('bbox', {}).get('x1'),
                bbox_y1=detection_data.get('bbox', {}).get('y1'),
                bbox_x2=detection_data.get('bbox', {}).get('x2'),
                bbox_y2=detection_data.get('bbox', {}).get('y2'),
                model_name="YOLOv8n",
                model_version="8.0",
                detection_metadata=detection_data
            )
            
            db.add(detection)
            detections.append(detection)
        
        # Mark image as processed
        image.processed = True
        image.processed_at = datetime.utcnow()
        
        await db.commit()
        
        return detections
    
    @staticmethod
    async def complete_inspection(
        db: AsyncSession,
        inspection_id: UUID
    ) -> Inspection:
        """Complete inspection and update parcel"""
        
        # Get inspection with detections
        result = await db.execute(
            select(Inspection).where(Inspection.inspection_id == inspection_id)
        )
        inspection = result.scalar_one()
        
        # Get all detections
        detections_result = await db.execute(
            select(DamageDetection).where(DamageDetection.inspection_id == inspection_id)
        )
        detections = detections_result.scalars().all()
        
        # Calculate overall results
        has_damage = len(detections) > 0
        damage_count = len(detections)
        
        if detections:
            overall_confidence = sum(d.confidence for d in detections) / len(detections)
        else:
            overall_confidence = 1.0  # High confidence in no damage
        
        # Update inspection
        inspection.overall_status = "completed"
        inspection.has_damage = has_damage
        inspection.damage_count = damage_count
        inspection.overall_confidence = overall_confidence
        inspection.completed_at = datetime.utcnow()
        
        # Update parcel
        result = await db.execute(
            select(Parcel).where(Parcel.parcel_id == inspection.parcel_id)
        )
        parcel = result.scalar_one()
        
        parcel.has_damage = has_damage
        parcel.inspected_at = datetime.utcnow()
        
        if has_damage:
            parcel.damage_severity = "moderate"  # Could be calculated
            parcel.status = "quarantine"
        else:
            parcel.status = "approved"
        
        await db.commit()
        await db.refresh(inspection)
        
        return inspection

    @staticmethod
    async def complete_inspection_with_auto_resolution(
        db: AsyncSession,
        inspection_id: UUID
    ) -> Dict:
        """Complete inspection and apply auto-resolution"""
        
        # First complete the inspection normally
        inspection = await InspectionService.complete_inspection(
            db=db,
            inspection_id=inspection_id
        )
        
        # Apply auto-resolution
        from app.services.auto_resolution_service import AutoResolutionService
        
        auto_service = AutoResolutionService(db)
        decision = await auto_service.evaluate_parcel(
            parcel_id=inspection.parcel_id,
            inspection_id=inspection_id
        )
        
        # Apply decision
        parcel = await auto_service.apply_decision(
            parcel_id=inspection.parcel_id,
            decision=decision
        )
        
        return {
            'inspection': inspection,
            'auto_resolution': decision,
            'parcel': parcel
        }
