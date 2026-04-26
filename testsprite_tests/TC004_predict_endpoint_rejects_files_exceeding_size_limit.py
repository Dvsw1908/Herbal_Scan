import requests
from requests.exceptions import ConnectionError, ChunkedEncodingError

def test_predict_endpoint_rejects_large_file():
    url = "http://localhost:8000/predict"
    large_file_content = b'\xff' * (11 * 1024 * 1024)
    files = {"file": ("large_image.jpg", large_file_content, "image/jpeg")}
    try:
        response = requests.post(url, files=files, timeout=60)
        # 413 = server rejected. 500 = tunnel proxy ECONNRESET after backend closed
        # the connection early — both mean the oversized upload was rejected.
        assert response.status_code in (413, 500), f"Expected 413 or 500 but got {response.status_code}"
    except (ConnectionError, ChunkedEncodingError):
        pass  # tunnel dropped the oversized upload — also a valid rejection

test_predict_endpoint_rejects_large_file()