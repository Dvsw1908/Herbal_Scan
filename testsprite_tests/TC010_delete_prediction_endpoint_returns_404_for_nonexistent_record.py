import requests

BASE_URL = "http://localhost:8000"

def test_delete_prediction_endpoint_returns_404_for_nonexistent_record():
    nonexistent_id = 99999999
    url = f"{BASE_URL}/history/{nonexistent_id}"
    try:
        response = requests.delete(url, timeout=30)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"
    assert response.status_code == 404, f"Expected status 404 but got {response.status_code}"
    try:
        resp_json = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"
    assert resp_json.get("detail") == "Data tidak ditemukan.", f"Expected detail 'Data tidak ditemukan.' but got {resp_json.get('detail')}"

test_delete_prediction_endpoint_returns_404_for_nonexistent_record()