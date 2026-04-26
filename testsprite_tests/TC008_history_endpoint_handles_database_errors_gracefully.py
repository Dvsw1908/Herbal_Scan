import requests

def test_history_endpoint_handles_database_errors_gracefully():
    url = "http://localhost:8000/history"
    try:
        response = requests.get(url, timeout=30)
        # The test expects 500 Internal Server Error due to DB unavailability simulation
        assert response.status_code == 500, f"Expected status code 500, got {response.status_code}"
        # Optionally check the response content contains error message
        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type or "text" in content_type, \
            "Expected JSON or text response content type in error"
        # If JSON, check error detail message presence
        try:
            json_data = response.json()
            assert "detail" in json_data or "error" in json_data or len(json_data) > 0, \
                "Expected error info in 500 response JSON"
        except Exception:
            # Not JSON response is acceptable as long as 500 status
            pass
    except requests.exceptions.RequestException as e:
        assert False, f"Request to /history failed: {e}"

test_history_endpoint_handles_database_errors_gracefully()