"""OCR service for reading shipping labels and text from images"""
import pytesseract
from PIL import Image
from typing import Dict, List, Optional
import re
from pathlib import Path

class OCRService:
    """Service for extracting text from images"""
    
    def __init__(self):
        """Initialize OCR service"""
        self.tracking_patterns = [
            r'1Z[0-9A-Z]{16}',  # UPS
            r'\d{12}',           # FedEx (12 digits)
            r'\d{20,22}',        # USPS
            r'[A-Z]{2}\d{9}[A-Z]{2}',  # DHL
        ]
    
    def extract_text(self, image_path: str) -> Dict:
        """
        Extract all text from image using Tesseract
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dict with extracted text and confidence
        """
        try:
            # Open image
            img = Image.open(image_path)
            
            # Extract text with detailed data
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            
            # Get full text
            full_text = pytesseract.image_to_string(img)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'success': True,
                'text': full_text,
                'confidence': avg_confidence / 100,  # Convert to 0-1 scale
                'word_count': len(full_text.split()),
                'raw_data': data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0.0
            }
    
    def extract_tracking_number(self, text: str) -> Optional[Dict]:
        """
        Extract tracking number from text using patterns
        
        Args:
            text: OCR extracted text
            
        Returns:
            Dict with tracking number and carrier if found
        """
        for pattern in self.tracking_patterns:
            match = re.search(pattern, text)
            if match:
                tracking_num = match.group(0)
                carrier = self._identify_carrier(tracking_num)
                
                return {
                    'tracking_number': tracking_num,
                    'carrier': carrier,
                    'confidence': 0.8  # Pattern match confidence
                }
        
        return None
    
    def _identify_carrier(self, tracking_num: str) -> str:
        """Identify carrier from tracking number format"""
        if tracking_num.startswith('1Z'):
            return 'UPS'
        elif len(tracking_num) == 12 and tracking_num.isdigit():
            return 'FedEx'
        elif len(tracking_num) in [20, 21, 22] and tracking_num.isdigit():
            return 'USPS'
        elif re.match(r'[A-Z]{2}\d{9}[A-Z]{2}', tracking_num):
            return 'DHL'
        else:
            return 'Unknown'
    
    def extract_label_info(self, image_path: str) -> Dict:
        """
        Extract shipping label information
        
        Args:
            image_path: Path to shipping label image
            
        Returns:
            Extracted label information
        """
        # Extract text
        ocr_result = self.extract_text(image_path)
        
        if not ocr_result['success']:
            return ocr_result
        
        text = ocr_result['text']
        
        # Extract tracking number
        tracking_info = self.extract_tracking_number(text)
        
        # Extract other common fields
        label_info = {
            'success': True,
            'tracking_number': tracking_info['tracking_number'] if tracking_info else None,
            'carrier': tracking_info['carrier'] if tracking_info else None,
            'raw_text': text,
            'ocr_confidence': ocr_result['confidence'],
            'dimensions': self._extract_dimensions(text),
            'weight': self._extract_weight(text)
        }
        
        return label_info
    
    def _extract_dimensions(self, text: str) -> Optional[Dict]:
        """Extract package dimensions from text"""
        # Look for patterns like "12x10x8" or "12 x 10 x 8"
        pattern = r'(\d+\.?\d*)\s*[xX×]\s*(\d+\.?\d*)\s*[xX×]\s*(\d+\.?\d*)'
        match = re.search(pattern, text)
        
        if match:
            return {
                'length': float(match.group(1)),
                'width': float(match.group(2)),
                'height': float(match.group(3)),
                'unit': 'cm'  # Assume cm, could be improved
            }
        
        return None
    
    def _extract_weight(self, text: str) -> Optional[Dict]:
        """Extract package weight from text"""
        # Look for patterns like "5.2 kg" or "10 lbs"
        patterns = [
            (r'(\d+\.?\d*)\s*kg', 'kg'),
            (r'(\d+\.?\d*)\s*lbs?', 'lbs'),
            (r'(\d+\.?\d*)\s*g\b', 'g')
        ]
        
        for pattern, unit in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    'value': float(match.group(1)),
                    'unit': unit
                }
        
        return None

# Singleton instance
_ocr_service: Optional[OCRService] = None

def get_ocr_service() -> OCRService:
    """Get singleton instance of OCR service"""
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service
