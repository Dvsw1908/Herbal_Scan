import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_history_endpoint_returns_all_prediction_records():
    url = f"{BASE_URL}/history"
    try:
        response = requests.get(url, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to {url} failed with exception: {e}"

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    try:
        data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    assert isinstance(data, list), f"Expected response to be a list but got {type(data)}"

    if len(data) > 0:
        for record in data:
            assert isinstance(record, dict), f"Each record should be a dict, got {type(record)}"
            assert "id" in record, "Record missing 'id'"
            assert isinstance(record["id"], int), "'id' should be int"
            assert "image_path" in record, "Record missing 'image_path'"
            assert isinstance(record["image_path"], str), "'image_path' should be str"
            assert "predicted_class" in record, "Record missing 'predicted_class'"
            assert isinstance(record["predicted_class"], str), "'predicted_class' should be str"
            assert "confidence_score" in record, "Record missing 'confidence_score'"
            assert isinstance(record["confidence_score"], float), "'confidence_score' should be float"
            assert "timestamp" in record, "Record missing 'timestamp'"
            assert isinstance(record["timestamp"], str), "'timestamp' should be str"
    else:
        # The API can validly return an empty array when no records exist
        assert data == [], "Expected empty list when no prediction records exist"

test_history_endpoint_returns_all_prediction_records()