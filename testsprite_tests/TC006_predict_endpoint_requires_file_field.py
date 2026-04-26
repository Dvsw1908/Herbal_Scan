import requests

def test_predict_endpoint_requires_file_field():
    url = "http://localhost:8000/predict"
    try:
        response = requests.post(url, files={}, timeout=30)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 422, f"Expected status code 422 but got {response.status_code}"
    try:
        resp_json = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    # The response should indicate a validation error for missing 'file' field
    # FastAPI returns validation errors under 'detail' as a list
    assert "detail" in resp_json, "Response JSON missing 'detail' field"
    detail = resp_json["detail"]
    assert isinstance(detail, list) and len(detail) > 0, "'detail' should be a non-empty list"
    # Checking that one of the errors is about 'file' field missing
    file_error_found = any(
        error.get("loc") == ["body", "file"] or ("file" in str(error))
        for error in detail
    )
    assert file_error_found, "Validation error for missing 'file' field not found in response detail"

test_predict_endpoint_requires_file_field()