"""
Augmentasi Dataset Daun Herbal
- Input : data/resized  (gambar 224x224 hasil resize)
- Output: data/augmented
- Tahap 1: 250 H-Flip + 250 V-Flip = 500 gambar dari original
- Tahap 2: Rotasi 500 hasil flip dengan 4 sudut (0/90/180/270) x 125 = 500 gambar
- Total augmented per kelas: 1000 | Total dengan original: 1300
"""
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

AUG_H_FLIP    = 250
AUG_V_FLIP    = 250
ROTATE_ANGLES = [0, 90, 180, 270]
ROT_PER_ANGLE = 125

VALID_EXTS = {".jpg", ".jpeg", ".png"}

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def rotate_image(img: np.ndarray, angle: int) -> np.ndarray:
    if angle == 0:
        return img.copy()
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REFLECT)


def format_time(seconds: float) -> str:
    return f"{int(seconds // 60)} menit {int(seconds % 60)} detik"


print("Mulai augmentasi per kelas")
print(f"Tahap 1 — H-Flip: {AUG_H_FLIP} | V-Flip: {AUG_V_FLIP} = {AUG_H_FLIP + AUG_V_FLIP} flip")
print(f"Tahap 2 — Rotasi {ROTATE_ANGLES} x {ROT_PER_ANGLE} = {len(ROTATE_ANGLES) * ROT_PER_ANGLE} rotasi")
print(f"Total augmented per kelas: {AUG_H_FLIP + AUG_V_FLIP + len(ROTATE_ANGLES) * ROT_PER_ANGLE}")
print(f"Input  : {INPUT_DIR}")
print(f"Output : {OUTPUT_DIR}")

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

    # ===== TAHAP 1: FLIP dari original =====
    flipped_paths = []

    count = 0
    while count < AUG_H_FLIP:
        img = cv2.imread(str(random.choice(images)))
        if img is None:
            continue
        out_path = out_cls / f"{cls_dir.name}_hflip_{count}.jpg"
        cv2.imwrite(str(out_path), cv2.flip(img, 1))
        flipped_paths.append(out_path)
        count += 1
        total_augmented += 1

    count = 0
    while count < AUG_V_FLIP:
        img = cv2.imread(str(random.choice(images)))
        if img is None:
            continue
        out_path = out_cls / f"{cls_dir.name}_vflip_{count}.jpg"
        cv2.imwrite(str(out_path), cv2.flip(img, 0))
        flipped_paths.append(out_path)
        count += 1
        total_augmented += 1

    # ===== TAHAP 2: ROTASI dari hasil flip =====
    rot_idx = 0
    for angle in ROTATE_ANGLES:
        count = 0
        while count < ROT_PER_ANGLE:
            img = cv2.imread(str(random.choice(flipped_paths)))
            if img is None:
                continue
            out_path = out_cls / f"{cls_dir.name}_rot{angle}_{rot_idx}.jpg"
            cv2.imwrite(str(out_path), rotate_image(img, angle))
            rot_idx += 1
            count += 1
            total_augmented += 1

    flip_total = AUG_H_FLIP + AUG_V_FLIP
    rot_total  = len(ROTATE_ANGLES) * ROT_PER_ANGLE
    print(f"  {cls_dir.name}: {flip_total} flip + {rot_total} rotasi = {flip_total + rot_total} augmented")

elapsed = time.time() - start_time

print()
print("Augmentasi selesai")
print(f"Total gambar dihasilkan : {total_augmented}")
print(f"Waktu proses            : {format_time(elapsed)}")
if skipped_classes:
    print(f"Kelas dilewati          : {skipped_classes}")
