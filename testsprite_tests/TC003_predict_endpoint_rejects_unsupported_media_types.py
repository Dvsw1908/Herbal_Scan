import requests

def test_predict_endpoint_rejects_unsupported_media_types():
    url = "http://localhost:8000/predict"

    # Prepare a text file content to simulate unsupported media type upload
    files = {
        'file': ('notes.txt', b'This is a plain text file, not an image.', 'text/plain')
    }

    try:
        response = requests.post(url, files=files, timeout=30)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 415, f"Expected status code 415, got {response.status_code}"
    # The API may return a plain message or JSON with error detail, verify content includes 'Unsupported Media Type'
    content_type = response.headers.get('Content-Type', '')
    if 'application/json' in content_type:
        try:
            data = response.json()
            # Could assert error message or detail field if present
            # Accept 'unsupported' or Indonesian equivalent 'tidak didukung'
            assert any(('unsupported' in str(v).lower() or 'tidak didukung' in str(v).lower()) for v in data.values()), f"Unexpected response content: {data}"
        except Exception:
            assert False, "Response JSON parse failed"
    else:
        # For non-json response body check common text presence
        assert 'unsupported media type' in response.text.lower()

test_predict_endpoint_rejects_unsupported_media_types()
