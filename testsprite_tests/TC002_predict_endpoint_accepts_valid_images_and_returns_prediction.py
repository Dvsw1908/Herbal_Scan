import requests
import io
from PIL import Image
import random

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def create_test_image(format: str, size_kb: int = 100) -> bytes:
    """
    Create a simple RGB image in memory with the specified format and approximate size in KB.
    The image will be a single-color image, size adjusted to reach the target size.
    """
    # Determine approximate dimensions to reach target size (rough estimate)
    # JPEG/WEBP compression varies; PNG is lossless; adjust size approximately.
    # 1 pixel ~ 3 bytes (RGB), adjust dimensions accordingly.
    # Let's just create a 256x256 image (approx 196KB raw), then adjust quality/compression
    img = Image.new("RGB", (256, 256), color=(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
    img_bytes = io.BytesIO()
    save_params = {}
    if format.lower() == "jpeg":
        save_params = {"format": "JPEG", "quality": 85}
    elif format.lower() == "png":
        save_params = {"format": "PNG"}
    elif format.lower() == "webp":
        save_params = {"format": "WEBP", "quality": 85}
    else:
        raise ValueError(f"Unsupported image format for test creation: {format}")

    img.save(img_bytes, **save_params)
    content = img_bytes.getvalue()
    # If too large, crop or resize (not critical as long it is under 10MB)
    if len(content) > size_kb * 1024:
        # Resize to smaller if needed
        scale = (size_kb * 1024) / len(content)
        new_size = max(1, int(256 * scale**0.5))
        img = img.resize((new_size, new_size))
        img_bytes = io.BytesIO()
        img.save(img_bytes, **save_params)
        content = img_bytes.getvalue()
    return content

def test_predict_endpoint_accepts_valid_images_and_returns_prediction():
    image_formats = [
        ("jpeg", "image/jpeg"),
        ("png", "image/png"),
        ("webp", "image/webp"),
    ]
    created_ids = []
    try:
        for ext, mime in image_formats:
            file_content = create_test_image(ext, size_kb=900)  # under 10MB limit
            files = {
                "file": (f"leaf.{ext}", io.BytesIO(file_content), mime)
            }
            response = requests.post(f"{BASE_URL}/predict", files=files, timeout=TIMEOUT)
            assert response.status_code == 200, f"Expected 200 OK for {ext}, got {response.status_code}"
            json_response = response.json()
            assert isinstance(json_response, dict), f"Response JSON is not an object for {ext}"
            assert "id" in json_response and isinstance(json_response["id"], int), f"Missing or invalid 'id' in response for {ext}"
            assert "predicted_class" in json_response and isinstance(json_response["predicted_class"], str), f"Missing or invalid 'predicted_class' for {ext}"
            assert "confidence_score" in json_response and isinstance(json_response["confidence_score"], (float, int)), f"Missing or invalid 'confidence_score' for {ext}"
            created_ids.append(json_response["id"])

        # After all predictions, check GET /history includes these ids
        history_resp = requests.get(f"{BASE_URL}/history", timeout=TIMEOUT)
        assert history_resp.status_code == 200, f"Expected 200 OK on /history, got {history_resp.status_code}"
        history_json = history_resp.json()
        assert isinstance(history_json, list), "/history response is not a list"
        history_ids = {entry.get("id") for entry in history_json if "id" in entry}

        for pred_id in created_ids:
            assert pred_id in history_ids, f"Prediction id {pred_id} not found in /history"

    finally:
        # Cleanup created prediction records
        for pred_id in created_ids:
            del_resp = requests.delete(f"{BASE_URL}/history/{pred_id}", timeout=TIMEOUT)
            # Deletion might fail if already deleted, but ignore here