import requests

def test_predict_endpoint_rejects_corrupt_or_unreadable_images():
    url = "http://localhost:8000/predict"
    # Prepare corrupt image bytes (random bytes, not a valid image)
    corrupt_image_content = b'\x00\x11\x22\x33\x44\x55\x66\x77\x88\x99\xaa\xbb\xcc\xdd\xee\xff' * 1000
    files = {
        'file': ('corrupt.jpg', corrupt_image_content, 'image/jpeg')
    }
    try:
        response = requests.post(url, files=files, timeout=30)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"
    assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
    try:
        json_resp = response.json()
    except Exception:
        json_resp = None
    if json_resp:
        # Accept English or localized Indonesian message indicating invalid image
        if isinstance(json_resp, dict):
            error_detail = json_resp.get('detail', '').lower()
            msg = str(json_resp).lower()
            assert (("invalid" in msg and "image" in msg) or "corrupt" in msg or "unreadable" in msg 
                    or "file bukan gambar yang valid" in error_detail), \
                f"Response JSON does not indicate invalid/corrupt image: {json_resp}"
        else:
            msg = str(json_resp).lower()
            assert (("invalid" in msg and "image" in msg) or "corrupt" in msg or "unreadable" in msg), \
                f"Response JSON does not indicate invalid/corrupt image: {json_resp}"
    else:
        text = response.text.lower()
        assert (("invalid" in text and "image" in text) or "corrupt" in text or "unreadable" in text 
                or "file bukan gambar yang valid" in text), \
            f"Response text does not indicate invalid/corrupt image: {response.text}"

test_predict_endpoint_rejects_corrupt_or_unreadable_images()
