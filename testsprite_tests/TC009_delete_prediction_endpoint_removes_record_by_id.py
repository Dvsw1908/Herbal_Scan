import base64
import io
import requests

VALID_JPEG_B64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAKAAoDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDnqKKKwPDP/9k="


def test_delete_prediction_endpoint_removes_record_by_id():
    base_url = "http://localhost:8000"
    # Decode base64 and prepare image file for upload
    image_bytes = io.BytesIO(base64.b64decode(VALID_JPEG_B64))
    files = {"file": ("leaf.jpg", image_bytes, "image/jpeg")}
    timeout = 30

    # Create a prediction to get a valid prediction_id
    response_predict = requests.post(f"{base_url}/predict", files=files, timeout=timeout)
    assert response_predict.status_code == 200, f"Expected 200 but got {response_predict.status_code}"
    predict_json = response_predict.json()
    assert "id" in predict_json, "Response JSON missing 'id'"
    prediction_id = predict_json["id"]

    try:
        # Delete the created prediction by id
        response_delete = requests.delete(f"{base_url}/history/{prediction_id}", timeout=timeout)
        assert response_delete.status_code == 200, f"Expected 200 but got {response_delete.status_code}"
        delete_json = response_delete.json()
        assert delete_json.get("message", "") == "Data berhasil dihapus.", f"Unexpected delete message: {delete_json}"

        # Verify the deleted prediction does not exist in GET /history
        response_history = requests.get(f"{base_url}/history", timeout=timeout)
        assert response_history.status_code == 200, f"Expected 200 but got {response_history.status_code}"
        history = response_history.json()
        assert all(record.get("id") != prediction_id for record in history), "Deleted prediction id still present in history"
    finally:
        # Ensure cleanup in case delete failed
        requests.delete(f"{base_url}/history/{prediction_id}", timeout=timeout)


test_delete_prediction_endpoint_removes_record_by_id()