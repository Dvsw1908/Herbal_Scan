import requests
from io import BytesIO

def test_predict_endpoint_rejects_corrupt_images():
    base_url = "http://localhost:8000"
    url = f"{base_url}/predict"
    timeout = 30

    # Create a byte sequence that represents a corrupt/unreadable JPEG image (invalid image data)
    corrupt_image_bytes = b"\xff\xd8\xff\xe0" + b"corruptdata" * 10 + b"\xff\xd9"

    files = {
        'file': ('corrupt.jpg', BytesIO(corrupt_image_bytes), 'image/jpeg')
    }

    try:
        response = requests.post(url, files=files, timeout=timeout)
    except requests.RequestException as e:
        assert False, f"Request to {url} failed with exception: {e}"

    assert response.status_code == 400, f"Expected HTTP 400 but got {response.status_code}"

    # The API returns a plain text or JSON error message indicating invalid image file
    # Try to parse JSON if possible; fallback to text
    try:
        data = response.json()
        # Check message presence and content indicative of invalid image file
        assert (
            "invalid" in data.get("detail", "").lower() 
            or "corrupt" in data.get("detail", "").lower()
            or "unreadable" in data.get("detail", "").lower()
            or "file bukan gambar yang valid" in data.get("detail", "").lower()
        ), f"Response JSON detail does not indicate invalid image: {data}"
    except ValueError:
        # Not JSON, check text content directly
        text = response.text.lower()
        assert "invalid" in text or "corrupt" in text or "unreadable" in text or "file bukan gambar yang valid" in text, f"Response text does not indicate invalid image: {response.text}"

test_predict_endpoint_rejects_corrupt_images()
