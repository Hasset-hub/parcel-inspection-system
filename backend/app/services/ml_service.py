"""
Mock ML Service - Instant Damage Detection for Development
"""

from typing import List, Dict, Optional, Any
import random
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DamageDetectionService:
    """Mock damage detection service with instant responses"""
    
    def __init__(self):
        """Initialize mock service"""
        self.model_loaded = True
        self.device = "mock-cpu"
        self.model_name = "YOLOv8n-Mock"
        
        # Damage types we can simulate
        self.damage_types = [
            "torn_cardboard",
            "crushed_corner", 
            "dent",
            "puncture",
            "water_damage",
            "torn_label",
            "scratches"
        ]
        
        logger.info("✅ Mock ML Service initialized (instant responses)")
    
    def analyze_damage(
        self, 
        image_path: str,
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """Mock damage analysis - returns instant fake results"""
        # Simulate minimal processing time
        time.sleep(random.uniform(0.1, 0.3))
        
        # 60% chance of damage detection
        has_damage = random.random() < 0.6
        
        detections = []
        damage_count = 0
        max_confidence = 0.0
        primary_damage_type = "no_damage"
        
        if has_damage:
            # Simulate 1-3 damage detections
            damage_count = random.randint(1, 3)
            primary_damage_type = random.choice(self.damage_types)
            
            for i in range(damage_count):
                confidence = random.uniform(confidence_threshold, 0.98)
                max_confidence = max(max_confidence, confidence)
                
                # Random bounding box coordinates (normalized 0-1)
                x1 = random.uniform(0, 0.7)
                y1 = random.uniform(0, 0.7)
                x2 = x1 + random.uniform(0.1, 0.3)
                y2 = y1 + random.uniform(0.1, 0.3)
                
                detection = {
                    'class_name': random.choice(self.damage_types),
                    'confidence': round(confidence, 3),
                    'bbox': {
                        'x1': round(x1, 3),
                        'y1': round(y1, 3),
                        'x2': round(x2, 3),
                        'y2': round(y2, 3)
                    },
                    'area': round((x2 - x1) * (y2 - y1), 3)
                }
                detections.append(detection)
        
        # Calculate overall damage score
        damage_score = max_confidence if has_damage else 0.0
        
        # Determine severity based on score
        if damage_score > 0.8:
            severity = "severe"
        elif damage_score > 0.6:
            severity = "moderate"
        elif damage_score > 0.4:
            severity = "minor"
        else:
            severity = "none"
        
        result = {
            'has_damage': has_damage,
            'damage_score': round(damage_score, 3),
            'damage_type': primary_damage_type,
            'severity': severity,
            'damage_count': damage_count,
            'detection_count': damage_count,  # ← ADDED THIS (same as damage_count)
            'detections': detections,
            'confidence_threshold': confidence_threshold,
            'model_info': {
                'name': self.model_name,
                'device': self.device,
                'mock': True
            },
            'processing_time_ms': random.randint(100, 300)
        }
        
        logger.info(
            f"Mock detection: {has_damage=}, score={damage_score:.3f}, "
            f"detections={damage_count}"
        )
        
        return result
    
    def analyze_batch(
        self,
        image_paths: List[str],
        confidence_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Analyze multiple images in batch"""
        results = []
        for image_path in image_paths:
            result = self.analyze_damage(image_path, confidence_threshold)
            results.append(result)
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get mock model information"""
        return {
            'model_type': self.model_name,
            'version': '1.0.0-mock',
            'device': self.device,
            'status': 'ready',
            'mock': True,
            'supported_damage_types': self.damage_types,
            'num_classes': len(self.damage_types),
            'confidence_threshold': 0.5,
            'input_size': (640, 640),
            'notes': 'Mock service for development - returns fake detections'
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check if mock service is working"""
        return {
            'status': 'healthy',
            'model_loaded': self.model_loaded,
            'device': self.device,
            'mock': True,
            'ready': True
        }


# Singleton instance
_service_instance: Optional[DamageDetectionService] = None


def get_damage_detection_service() -> DamageDetectionService:
    """Get singleton instance of damage detection service"""
    global _service_instance
    if _service_instance is None:
        _service_instance = DamageDetectionService()
    return _service_instance


def get_ml_service() -> DamageDetectionService:
    """Alias for get_damage_detection_service()"""
    return get_damage_detection_service()
