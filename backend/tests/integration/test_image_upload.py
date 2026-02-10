"""Test image upload endpoints"""
import pytest
from httpx import AsyncClient
from app.main import app
from PIL import Image
import io

@pytest.mark.asyncio
async def test_upload_single_image():
    """Test single image upload"""
    # Create test image
    img = Image.new('RGB', (800, 600), color='blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/images/upload",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "filename" in data
        assert "path" in data
        assert data["size"] > 0

@pytest.mark.asyncio
async def test_upload_multiple_images():
    """Test multiple image upload"""
    files = []
    
    # Create 3 test images
    for i in range(3):
        img = Image.new('RGB', (800, 600), color=['red', 'green', 'blue'][i])
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        files.append(("files", (f"test{i}.jpg", img_bytes, "image/jpeg")))
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/images/upload-multiple",
            files=files
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 3
        assert len(data["files"]) == 3

@pytest.mark.asyncio
async def test_invalid_file_type():
    """Test upload rejects non-image files"""
    # Create text file
    text_bytes = io.BytesIO(b"This is not an image")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/images/upload",
            files={"file": ("test.txt", text_bytes, "text/plain")}
        )
        
        assert response.status_code == 400
