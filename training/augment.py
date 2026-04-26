"""
Augmentasi Dataset Daun Herbal
- Input : data/resized  (gambar 224x224 hasil resize)
- Output: data/augmented
- Per kelas: 167 H-Flip + 167 V-Flip + 166 Random Rotate (±30°) = 500 gambar
- Dengan 300 data asli → total 800 per kelas
- Border rotasi: REFLECT agar tidak ada piksel hitam di sudut
"""
import os
import cv2
import time
import random
import numpy as np
from pathlib import Path

# =====================
# CONFIG
# =====================
BASE_DIR   = Path(__file__).resolve().parent
INPUT_DIR  = BASE_DIR.parent / "data" / "resized"
OUTPUT_DIR = BASE_DIR.parent / "data" / "augmented"

AUG_H_FLIP = 167
AUG_V_FLIP = 167
AUG_ROTATE = 166
MAX_ANGLE  = 30

VALID_EXTS = {".jpg", ".jpeg", ".png"}

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def rotate_image(img: np.ndarray, angle: float) -> np.ndarray:
    """Rotasi gambar dengan pusat di tengah, border di-reflect agar tidak ada piksel hitam."""
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REFLECT)


def format_time(seconds: float) -> str:
    return f"{int(seconds // 60)} menit {int(seconds % 60)} detik"


print("Mulai augmentasi per kelas")
print(f"H-Flip: {AUG_H_FLIP} | V-Flip: {AUG_V_FLIP} | Rotate: {AUG_ROTATE} | Total: {AUG_H_FLIP + AUG_V_FLIP + AUG_ROTATE} per kelas")
print(f"Input  : {INPUT_DIR}")
print(f"Output : {OUTPUT_DIR}")
print()

start_time      = time.time()
total_augmented = 0
skipped_classes = []

for cls_dir in sorted(INPUT_DIR.iterdir()):
    if not cls_dir.is_dir():
        continue

    out_cls = OUTPUT_DIR / cls_dir.name
    out_cls.mkdir(exist_ok=True)

    images = [p for p in cls_dir.iterdir() if p.suffix.lower() in VALID_EXTS]
    if not images:
        print(f"  Warning: {cls_dir.name} — tidak ada gambar, dilewati")
        skipped_classes.append(cls_dir.name)
        continue

    # ===== 167 HORIZONTAL FLIP =====
    count = 0
    while count < AUG_H_FLIP:
        img = cv2.imread(str(random.choice(images)))
        if img is None:
            continue
        cv2.imwrite(str(out_cls / f"{cls_dir.name}_hflip_{count}.jpg"), cv2.flip(img, 1))
        count += 1
        total_augmented += 1

    # ===== 167 VERTICAL FLIP =====
    count = 0
    while count < AUG_V_FLIP:
        img = cv2.imread(str(random.choice(images)))
        if img is None:
            continue
        cv2.imwrite(str(out_cls / f"{cls_dir.name}_vflip_{count}.jpg"), cv2.flip(img, 0))
        count += 1
        total_augmented += 1

    # ===== 166 RANDOM ROTATE =====
    count = 0
    while count < AUG_ROTATE:
        img = cv2.imread(str(random.choice(images)))
        if img is None:
            continue
        angle = random.uniform(-MAX_ANGLE, MAX_ANGLE)
        cv2.imwrite(str(out_cls / f"{cls_dir.name}_rot_{count}_{angle:.1f}deg.jpg"), rotate_image(img, angle))
        count += 1
        total_augmented += 1

    print(f"  {cls_dir.name}: {AUG_H_FLIP + AUG_V_FLIP + AUG_ROTATE} gambar augmentasi")

elapsed = time.time() - start_time

print()
print("Augmentasi selesai")
print(f"Total gambar dihasilkan : {total_augmented}")
print(f"Waktu proses            : {format_time(elapsed)}")
if skipped_classes:
    print(f"Kelas dilewati          : {skipped_classes}")
