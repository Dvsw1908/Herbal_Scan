"""
Membuat CSV yang mengikuti gambar di data/train_combined, tetapi tetap memakai
hasil prediksi dan confidence dari hasil_prediksi.csv lama.
"""

import csv
from collections import defaultdict
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SOURCE_CSV = ROOT_DIR / "hasil_prediksi.csv"
DATA_DIR = ROOT_DIR / "data" / "train_combined"
OUTPUT_CSV = ROOT_DIR / "hasil_prediksi_fixed.csv"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
COLUMNS = [
    "No",
    "Nama File",
    "Kelas Daun",
    "Prediksi Kelas Daun",
    "Confidence Score",
]


def normalize(value: str) -> str:
    return " ".join(value.lower().split())


def image_sort_key(path: Path) -> tuple[str, int]:
    stem = path.stem
    digits = "".join(ch for ch in stem if ch.isdigit())
    return (stem.rstrip("0123456789"), int(digits) if digits else 0)


def read_prediction_rows(csv_path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    headers = None

    with csv_path.open(newline="", encoding="utf-8") as file:
        for raw_row in csv.reader(file):
            if not raw_row or not any(cell.strip() for cell in raw_row):
                continue
            first_cell = raw_row[0].strip()
            if first_cell.startswith("#"):
                continue
            if raw_row[: len(COLUMNS)] == COLUMNS:
                headers = COLUMNS
                continue
            if headers is None:
                continue
            values = raw_row[: len(COLUMNS)]
            if values == COLUMNS:
                continue
            rows.append(dict(zip(COLUMNS, values)))

    return rows


def read_train_images(data_dir: Path) -> dict[str, list[Path]]:
    images_by_class: dict[str, list[Path]] = {}
    for class_dir in sorted(data_dir.iterdir(), key=lambda p: p.name.lower()):
        if not class_dir.is_dir():
            continue
        images = [
            path
            for path in class_dir.iterdir()
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        ]
        images_by_class[class_dir.name] = sorted(images, key=image_sort_key)
    return images_by_class


def main() -> None:
    source_rows = read_prediction_rows(SOURCE_CSV)
    rows_by_class: dict[str, list[dict[str, str]]] = defaultdict(list)
    display_class_by_key: dict[str, str] = {}

    for row in source_rows:
        class_name = row["Kelas Daun"].strip()
        key = normalize(class_name)
        rows_by_class[key].append(row)
        display_class_by_key.setdefault(key, class_name)

    output_rows = []
    train_images = read_train_images(DATA_DIR)
    warnings = []

    for actual_class, images in train_images.items():
        key = normalize(actual_class)
        prediction_rows = rows_by_class.get(key, [])
        if len(prediction_rows) < len(images):
            warnings.append(
                f"{actual_class}: prediksi {len(prediction_rows)}, gambar {len(images)}"
            )
            continue

        for index, image_path in enumerate(images):
            prediction_row = prediction_rows[index]
            output_rows.append(
                {
                    "No": len(output_rows) + 1,
                    "Nama File": image_path.name,
                    "Kelas Daun": actual_class,
                    "Prediksi Kelas Daun": prediction_row["Prediksi Kelas Daun"],
                    "Confidence Score": prediction_row["Confidence Score"],
                }
            )

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Sumber prediksi: {SOURCE_CSV}")
    print(f"Data output: {len(output_rows)}")
    print(f"CSV fixed tersimpan: {OUTPUT_CSV}")
    for warning in warnings:
        print(f"WARNING: {warning}")


if __name__ == "__main__":
    main()
