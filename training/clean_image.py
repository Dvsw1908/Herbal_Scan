import os
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "..", "data", "final")

deleted = 0

for root, _, files in os.walk(DATASET_DIR):
    for file in files:
        if file.lower().endswith((".jpg", ".png", ".jpeg")):
            path = os.path.join(root, file)
            try:
                with Image.open(path) as img:
                    img.verify()  # cek valid atau tidak
            except Exception:
                print(f"❌ Hapus file rusak: {path}")
                os.remove(path)
                deleted += 1

print(f"\n✅ Selesai. Total file rusak dihapus: {deleted}")