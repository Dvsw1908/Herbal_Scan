import requests
from requests.exceptions import RequestException

def test_predict_endpoint_rejects_unsupported_file_types():
    base_url = "http://localhost:8000"
    url = f"{base_url}/predict"
    # Prepare a dummy text file content with text/plain MIME type
    files = {
        "file": ("notes.txt", "This is a plain text file, not an image.", "text/plain")
    }
    try:
        response = requests.post(url, files=files, timeout=30)
    except RequestException as e:
        assert False, f"Request to /predict failed: {e}"

    # Assert that the response status code is 415 Unsupported Media Type
    assert response.status_code == 415, (
        f"Expected status code 415 for unsupported file type but got {response.status_code}. "
        f"Response content: {response.text}"
    )

test_predict_endpoint_rejects_unsupported_file_types()