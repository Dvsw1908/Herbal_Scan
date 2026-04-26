import requests

BASE_URL = "http://localhost:8000"

def test_delete_prediction_non_existent_id():
    non_existent_id = 99999999  # Assumed to not exist in DB
    url = f"{BASE_URL}/history/{non_existent_id}"
    try:
        response = requests.delete(url, timeout=30)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 404, f"Expected 404 but got {response.status_code}"
    json_response = response.json()
    assert "detail" in json_response, "Response JSON missing 'detail' key"
    assert json_response["detail"] == "Data tidak ditemukan.", f"Unexpected detail message: {json_response['detail']}"

test_delete_prediction_non_existent_id()