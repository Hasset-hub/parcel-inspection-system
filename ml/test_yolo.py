"""Test YOLO model on sample images"""
from ultralytics import YOLO
from pathlib import Path

def test_yolo():
    """Test YOLO model with our test images"""
    print("🧪 Testing YOLO Model...")
    
    # Load model
    model = YOLO('yolov8n.pt')
    print("✅ Model loaded")
    
    # Test images directory
    test_dir = Path('ml/test_images')
    
    if not test_dir.exists():
        print("❌ Test images directory not found")
        return
    
    # Get all image files
    image_files = list(test_dir.glob('*.jpg')) + list(test_dir.glob('*.png'))
    
    if not image_files:
        print("❌ No test images found")
        return
    
    print(f"\n📸 Found {len(image_files)} test images")
    
    # Run inference on each image
    for img_path in image_files:
        print(f"\n🔍 Analyzing: {img_path.name}")
        
        # Run inference
        results = model(str(img_path))
        
        # Get detections
        result = results[0]
        
        print(f"   Detections: {len(result.boxes)} objects found")
        
        # Print detected objects
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            class_name = result.names[class_id]
            
            print(f"   - {class_name}: {confidence:.2%} confidence")
        
        # Save annotated image
        output_path = test_dir / f"detected_{img_path.name}"
        result.save(str(output_path))
        print(f"   ✅ Saved annotated image: {output_path.name}")
    
    print("\n✅ YOLO test complete!")
    print(f"📁 Annotated images saved in: {test_dir}")

if __name__ == "__main__":
    test_yolo()
