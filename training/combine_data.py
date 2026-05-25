"""
Membuat hasil_prediksi.csv dari data/train_combined.

Logika:
1. Baca actual class dari nama folder di data/train_combined.
2. Loop gambar di dalam folder actual class tersebut.
3. Jalankan model untuk membuat prediksi.
4. Simpan CSV dengan format:
   No,Nama File,Kelas Daun,Prediksi Kelas Daun,Confidence Score
"""

from pathlib import Path

import pandas as pd
import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms


ROOT_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT_DIR / "model" / "shufflenet_exp2_80.pth"
DATA_DIR = ROOT_DIR / "data" / "train_combined"
OUTPUT_CSV = ROOT_DIR / "hasil_prediksi.csv"

CLASS_NAMES = [
    "Daun Alpukat BG",
    "Daun Alpukat NoBG",
    "Daun Alpukat Rusak BG",
    "Daun Alpukat Rusak NoBG",
    "Daun Belimbing Wuluh BG",
    "Daun Belimbing Wuluh NoBG",
    "Daun Belimbing Wuluh Rusak BG",
    "Daun Belimbing Wuluh Rusak NoBG",
    "Daun Jambu Biji Rusak BG",
    "Daun Jambu Biji Rusak NoBG",
    "Daun Jambu biji BG",
    "Daun Jambu biji NoBG",
    "Daun Leci BG",
    "Daun Leci NoBG",
    "Daun Leci Rusak BG",
    "Daun Leci Rusak NoBG",
    "Daun Nangka BG",
    "Daun Nangka NoBG",
    "Daun Nangka Rusak BG",
    "Daun Nangka Rusak NoBG",
    "Daun Salam BG",
    "Daun Salam NoBG",
    "Daun Salam Rusak BG",
    "Daun Salam Rusak NoBG",
    "Daun Sirsak BG",
    "Daun Sirsak NoBG",
    "Daun Sirsak Rusak BG",
    "Daun Sirsak Rusak NoBG",
    "Daun Srikaya BG",
    "Daun Srikaya NoBG",
    "Daun Srikaya Rusak BG",
    "Daun Srikaya Rusak NoBG",
]

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def image_sort_key(path: Path) -> tuple[str, int]:
    stem = path.stem
    number = "".join(ch for ch in stem if ch.isdigit())
    return (stem.rstrip("0123456789"), int(number) if number else 0)


def build_model() -> torch.nn.Module:
    model = models.shufflenet_v2_x1_0(weights=None)
    model.fc = nn.Linear(model.fc.in_features, len(CLASS_NAMES))
    state = torch.load(MODEL_PATH, map_location="cpu", weights_only=True)
    model.load_state_dict(state)
    model.eval()
    return model


def iter_images_by_actual_class(data_dir: Path):
    class_dirs = sorted([p for p in data_dir.iterdir() if p.is_dir()], key=lambda p: p.name.lower())
    for class_dir in class_dirs:
        images = [
            p
            for p in class_dir.iterdir()
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
        ]
        for image_path in sorted(images, key=image_sort_key):
            yield class_dir.name, image_path


def main() -> None:
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Folder data tidak ditemukan: {DATA_DIR}")
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model tidak ditemukan: {MODEL_PATH}")

    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )

    model = build_model()
    rows = []
    image_items = list(iter_images_by_actual_class(DATA_DIR))
    print(f"Ditemukan {len(image_items)} gambar dari {DATA_DIR}")

    for actual_class, image_path in image_items:
        image = Image.open(image_path).convert("RGB")
        tensor = transform(image).unsqueeze(0)

        with torch.no_grad():
            output = model(tensor)
            probabilities = torch.softmax(output, dim=1)
            confidence, pred_idx = torch.max(probabilities, dim=1)

        rows.append(
            {
                "No": len(rows) + 1,
                "Nama File": image_path.name,
                "Kelas Daun": actual_class,
                "Prediksi Kelas Daun": CLASS_NAMES[pred_idx.item()],
                "Confidence Score": f"{confidence.item() * 100:.2f}%",
            }
        )

        if len(rows) % 100 == 0:
            print(f"Progress: {len(rows)}/{len(image_items)}")

    output_path = OUTPUT_CSV
    try:
        pd.DataFrame(rows).to_csv(output_path, index=False, encoding="utf-8")
    except PermissionError:
        output_path = OUTPUT_CSV.with_name("hasil_prediksi_baru.csv")
        pd.DataFrame(rows).to_csv(output_path, index=False, encoding="utf-8")
        print(f"{OUTPUT_CSV.name} sedang terkunci, jadi hasil ditulis ke file baru.")

    print(f"Selesai. CSV tersimpan di: {output_path}")


if __name__ == "__main__":
    main()
