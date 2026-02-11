"""ML Service for YOLO damage detection"""
from ultralytics import YOLO
from typing import List, Dict, Optional
import os

class DamageDetectionService:
    """Service for detecting damage using YOLO"""
    
    def __init__(self, model_path: str = "yolov8n.pt"):
        """Initialize YOLO model"""
        self.model = YOLO(model_path)
        self.damage_keywords = [
            'damaged', 'broken', 'torn', 'crushed', 
            'dented', 'ripped', 'cracked'
        ]
    
    def detect_objects(self, image_path: str, confidence_threshold: float = 0.25) -> List[Dict]:
        """
        Detect objects in image
        
        Args:
            image_path: Path to image file
            confidence_threshold: Minimum confidence for detection
            
        Returns:
            List of detections with bounding boxes and confidence
        """
        # Run inference
        results = self.model(image_path)
        result = results[0]
        
        detections = []
        
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            
            if confidence < confidence_threshold:
                continue
            
            # Get bounding box coordinates
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            
            detection = {
                'class_id': class_id,
                'class_name': result.names[class_id],
                'confidence': confidence,
                'bbox': {
                    'x1': x1,
                    'y1': y1,
                    'x2': x2,
                    'y2': y2
                }
            }
            
            detections.append(detection)
        
        return detections
    
    def analyze_damage(self, image_path: str) -> Dict:
        """
        Analyze image for potential damage
        
        Returns:
            Analysis results with damage assessment
        """
        detections = self.detect_objects(image_path)
        
        # Simple damage detection logic
        # In production, you'd train a custom model
        has_damage = False
        damage_score = 0.0
        damage_regions = []
        
        if len(detections) == 0:
            # No recognizable objects - might indicate damage/obscured
            damage_score = 0.3
            has_damage = True
            damage_type = "unrecognizable_content"
        else:
            # Check confidence levels - low confidence might indicate damage
            avg_confidence = sum(d['confidence'] for d in detections) / len(detections)
            
            if avg_confidence < 0.5:
                damage_score = 0.6
                has_damage = True
                damage_type = "low_confidence_detection"
            else:
                damage_score = 0.0
                has_damage = False
                damage_type = "no_damage_detected"
        
        return {
            'has_damage': has_damage,
            'damage_score': damage_score,
            'damage_type': damage_type,
            'detections': detections,
            'detection_count': len(detections),
            'analyzed': True
        }
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        return {
            'model_type': 'YOLOv8n',
            'num_classes': len(self.model.names),
            'class_names': list(self.model.names.values()),
            'task': 'object detection'
        }

# Singleton instance
_damage_service: Optional[DamageDetectionService] = None

def get_damage_detection_service() -> DamageDetectionService:
    """Get singleton instance of damage detection service"""
    global _damage_service
    if _damage_service is None:
        _damage_service = DamageDetectionService()
    return _damage_service
