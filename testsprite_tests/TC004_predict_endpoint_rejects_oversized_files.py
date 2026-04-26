import requests

def test_predict_endpoint_rejects_oversized_files():
    url = "http://localhost:8000/predict"
    # Create a dummy file-like object with size > 10MB
    # 10MB = 10 * 1024 * 1024 = 10485760 bytes, create 12MB (12582912 bytes)
    size_in_bytes = 12 * 1024 * 1024
    oversized_content = b'\xff' * size_in_bytes

    files = {
        'file': ('huge.jpg', oversized_content, 'image/jpeg')
    }

    try:
        response = requests.post(url, files=files, timeout=30)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 413, f"Expected status code 413, got {response.status_code}"
    # The PRD indicates 413 returns message "File size exceeds 10 MB limit"
    # We check json message if possible, else text
    # Some servers may return plain text or JSON with error detail - we accept both
    try:
        data = response.json()
        # if response is structured, could have error message
        # but PRD states just "413: File size exceeds 10 MB limit"
        # We'll check any string presence
        assert any(
            msg in str(data).lower() for msg in ["payload too large", "file size", "exceeds 10 mb"]
        )
    except ValueError:
        # Not a JSON response - check text
        assert "payload too large" in response.text.lower() or "file size" in response.text.lower()

test_predict_endpoint_rejects_oversized_files()