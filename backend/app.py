from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
import io

from database import init_db, save_prediction, get_all_predictions, delete_prediction
from inference import predict_image

init_db()

app = FastAPI(title="HerbalScan Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE_MB = 10


@app.get("/")
def root():
    return {"status": "HerbalScan backend siap", "version": "1.0.0"}


@app.post("/predict")
async def predict(request: Request, file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Tipe file tidak didukung: {file.content_type}. Gunakan JPEG/PNG/WEBP.",
        )

    # Reject early using Content-Length header before reading the body
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > (MAX_FILE_SIZE_MB * 1024 * 1024) + 4096:
                raise HTTPException(
                    status_code=413,
                    detail=f"Ukuran file melebihi batas {MAX_FILE_SIZE_MB} MB.",
                )
        except ValueError:
            pass

    try:
        image_bytes = await file.read()
    except Exception:
        raise HTTPException(
            status_code=413,
            detail=f"Ukuran file melebihi batas {MAX_FILE_SIZE_MB} MB.",
        )

    if len(image_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"Ukuran file melebihi batas {MAX_FILE_SIZE_MB} MB.",
        )

    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.load()
        image = image.convert("RGB")
    except (UnidentifiedImageError, OSError, SyntaxError, Exception) as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=400, detail="File bukan gambar yang valid.")

    predicted_class, confidence_score = predict_image(image)

    record_id = save_prediction(
        image_path=file.filename or "unknown",
        predicted_class=predicted_class,
        confidence_score=confidence_score,
    )

    return {
        "id": record_id,
        "predicted_class": predicted_class,
        "confidence_score": round(confidence_score, 4),
    }


@app.get("/history")
def history():
    return get_all_predictions()


@app.delete("/history/{prediction_id}")
def delete_history(prediction_id: int):
    deleted = delete_prediction(prediction_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan.")
    return {"message": "Data berhasil dihapus."}
