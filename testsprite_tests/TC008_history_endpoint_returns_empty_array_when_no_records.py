import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_history_endpoint_returns_empty_array_when_no_records():
    url = f"{BASE_URL}/history"

    try:
        response = requests.get(url, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to GET /history failed: {e}"

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    try:
        data = response.json()
    except ValueError as e:
        assert False, f"Response is not valid JSON: {e}"

    assert isinstance(data, list), f"Expected response to be a list, got {type(data)}"
    assert len(data) == 0, f"Expected empty list when no records exist, got {len(data)} items"

test_history_endpoint_returns_empty_array_when_no_records()