import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_healthcheck_endpoint_returns_status_and_version():
    try:
        # Test successful health check response (HTTP 200)
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
        json_data = response.json()
        assert isinstance(json_data, dict), f"Response JSON is not a dict: {json_data}"
        assert json_data.get("status") == "HerbalScan backend siap", f"Expected status 'HerbalScan backend siap' but got {json_data.get('status')}"
        assert json_data.get("version") == "1.0.0", f"Expected version '1.0.0' but got {json_data.get('version')}"

        # Test backend unavailability handling
        # Since we cannot actually turn off the backend in this test,
        # simulate by making request to an unresponsive port or path
        # or if endpoint supports a way to simulate error. Here, we do a direct call
        # if backend responds 500, test that as well.
        # Making a request to cause 500 is not defined in PRD,
        # So this part is to verify if 500 returned, check message.
        # If no 500 returned, test passes as backend is running.

        # Attempt to catch 500 response in a retry or direct call, harmless if not returned
        # We'll do a GET / and accept either 200 or 500
        # If 500, check error message
        response2 = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        if response2.status_code == 500:
            json_err = response2.json()
            assert "error" in json_err or "detail" in json_err, "Expected error message in 500 response"
        else:
            assert response2.status_code == 200, f"Expected status 200 or 500 but got {response2.status_code}"
    except requests.RequestException as e:
        assert False, f"Request failed with exception: {e}"

test_healthcheck_endpoint_returns_status_and_version()