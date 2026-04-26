import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_health_check_endpoint_returns_status_and_version():
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to health check endpoint failed: {e}"

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    try:
        json_data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    assert "status" in json_data, "Response JSON missing 'status' field"
    assert "version" in json_data, "Response JSON missing 'version' field"

    assert isinstance(json_data["status"], str), "'status' field is not a string"
    assert isinstance(json_data["version"], str), "'version' field is not a string"

    expected_status = "HerbalScan backend siap"
    expected_version = "1.0.0"

    assert json_data["status"] == expected_status, f"Expected status '{expected_status}', got '{json_data['status']}'"
    assert json_data["version"] == expected_version, f"Expected version '{expected_version}', got '{json_data['version']}'"

test_health_check_endpoint_returns_status_and_version()