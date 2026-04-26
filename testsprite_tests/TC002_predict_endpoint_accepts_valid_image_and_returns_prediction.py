import requests
import base64
import io

BASE_URL = "http://localhost:8000"
VALID_JPEG_B64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAKAAoDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDnqKKKwPDP/9k="

def test_predict_endpoint_accepts_valid_image_and_returns_prediction():
    image_bytes = base64.b64decode(VALID_JPEG_B64)
    image_file = io.BytesIO(image_bytes)
    image_file.name = "leaf.jpg"
    files = {"file": ("leaf.jpg", image_file, "image/jpeg")}
    predict_url = f"{BASE_URL}/predict"

    # POST /predict with valid image
    response = requests.post(predict_url, files=files, timeout=30)
    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
    json_data = response.json()

    # Validate response JSON fields
    assert "id" in json_data and isinstance(json_data["id"], int), "Response missing 'id' or 'id' not int"
    assert "predicted_class" in json_data and isinstance(json_data["predicted_class"], str), "Response missing 'predicted_class' or not string"
    assert "confidence_score" in json_data and isinstance(json_data["confidence_score"], (float, int)), "Response missing 'confidence_score' or not a number"

    # Validate prediction stored in DB by checking /history includes the new id
    history_url = f"{BASE_URL}/history"
    history_response = requests.get(history_url, timeout=30)
    assert history_response.status_code == 200, f"Expected status code 200 on /history but got {history_response.status_code}"
    history_data = history_response.json()
    assert any(record.get("id") == json_data["id"] for record in history_data), "New prediction record is not found in /history"

test_predict_endpoint_accepts_valid_image_and_returns_prediction()