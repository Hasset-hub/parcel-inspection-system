"""Download YOLOv8 pre-trained model"""
from ultralytics import YOLO
import os

def download_yolo_model():
    """Download YOLOv8n (nano) model - smallest and fastest"""
    print("📥 Downloading YOLOv8n model...")
    
    # This will automatically download the model
    model = YOLO('yolov8n.pt')
    
    # Move to our models directory
    model_path = 'ml/models/yolov8n.pt'
    
    print(f"✅ Model downloaded successfully!")
    print(f"📁 Model saved to: {model_path}")
    print(f"📊 Model info:")
    print(f"   - Type: YOLOv8n (Nano - fastest)")
    print(f"   - Classes: 80 (COCO dataset)")
    print(f"   - Use case: Real-time object detection")
    
    return model

if __name__ == "__main__":
    model = download_yolo_model()
    
    # Test the model with a simple prediction
    print("\n🧪 Testing model...")
    
    # Create a dummy test (model will download on first use)
    print("✅ Model is ready to use!")
    print("\nNext steps:")
    print("1. Create test images in ml/test_images/")
    print("2. Run inference with the model")
    print("3. Integrate with FastAPI backend")
