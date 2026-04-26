import requests
import io

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_delete_prediction_endpoint_deletes_existing_record():
    # Step 1: Create a new prediction record by uploading a valid image
    # Using a minimal valid JPEG binary (1x1 px white pixel) as image content
    jpeg_image_bytes = (
        b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
        b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\x09\x09\x08'
        b'\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x19\x1f\x1e\x1d'
        b'\x19\x1c\x1c $.\' " ,#\x1c\x1c(%\x353),01444\x1f\'9=82<.342\xff\xc0\x00'
        b'\x11\x08\x00\x01\x00\x01\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4'
        b'\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00'
        b'\xd2\xcf \xff\xd9'
    )
    files = {'file': ('leaf.jpg', io.BytesIO(jpeg_image_bytes), 'image/jpeg')}

    try:
        response_post = requests.post(f"{BASE_URL}/predict", files=files, timeout=TIMEOUT)
        assert response_post.status_code == 200, f"POST /predict failed with status {response_post.status_code}"
        json_post = response_post.json()
        prediction_id = json_post.get("id")
        assert isinstance(prediction_id, int), "Response id is not an integer"
        assert "predicted_class" in json_post and isinstance(json_post["predicted_class"], str)
        assert "confidence_score" in json_post and isinstance(json_post["confidence_score"], float)

        # Step 2: Delete the created prediction record
        response_delete = requests.delete(f"{BASE_URL}/history/{prediction_id}", timeout=TIMEOUT)
        assert response_delete.status_code == 200, f"DELETE /history/{prediction_id} failed with status {response_delete.status_code}"
        json_delete = response_delete.json()
        assert "message" in json_delete and json_delete["message"] == "Data berhasil dihapus."

        # Step 3: Verify the deleted record is no longer in GET /history
        response_get = requests.get(f"{BASE_URL}/history", timeout=TIMEOUT)
        assert response_get.status_code == 200, f"GET /history failed with status {response_get.status_code}"
        history_list = response_get.json()
        assert isinstance(history_list, list), "GET /history response is not a list"
        ids = [record.get("id") for record in history_list if "id" in record]
        assert prediction_id not in ids, "Deleted prediction_id still present in GET /history response"

    finally:
        # Clean up: attempt to delete the prediction if it still exists (in case test failed before deletion)
        if 'prediction_id' in locals():
            try:
                requests.delete(f"{BASE_URL}/history/{prediction_id}", timeout=TIMEOUT)
            except Exception:
                pass

test_delete_prediction_endpoint_deletes_existing_record()
