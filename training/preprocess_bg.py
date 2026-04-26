"""
Preprocessing Dataset BG (Dengan Background)
- Input : data/raw  (gambar asli dengan background)
- Output: data/final bg
- Per kelas: copy+resize original + 167 H-Flip + 167 V-Flip + 166 Rotasi Kotak (0°/90°/180°/270°) = 500 augmented
- Total per kelas: ~300 original + 500 augmented = ~800
"""
import random
import time
import cv2
import numpy as np
from pathlib import Path

# =====================
# CONFIG
# =====================
BASE_DIR     = Path(__file__).resolve().parent
RAW_DIR      = BASE_DIR.parent / "data" / "raw"
FINAL_BG_DIR = BASE_DIR.parent / "data" / "final bg"

IMG_SIZE    = (224, 224)
AUG_H_FLIP  = 167
AUG_V_FLIP  = 167
AUG_ROTATE  = 166

VALID_EXTS  = {".jpg", ".jpeg", ".png"}
ROTATE_ANGLES = [cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE]

FINAL_BG_DIR.mkdir(parents=True, exist_ok=True)


def format_time(seconds: float) -> str:
    return f"{int(seconds // 60)} menit {int(seconds % 60)} detik"


print("Preprocess BG dimulai")
print(f"Input  : {RAW_DIR}")
print(f"Output : {FINAL_BG_DIR}")
print(f"Aug    : H-Flip={AUG_H_FLIP} | V-Flip={AUG_V_FLIP} | Rotasi Kotak={AUG_ROTATE}")
print()

start_time      = time.time()
total_original  = 0
total_augmented = 0

for cls_dir in sorted(RAW_DIR.iterdir()):
    if not cls_dir.is_dir():
        continue

    out_cls = FINAL_BG_DIR / cls_dir.name
    out_cls.mkdir(exist_ok=True)

    images = [p for p in cls_dir.iterdir() if p.suffix.lower() in VALID_EXTS]
    if not images:
        print(f"  Warning: {cls_dir.name} — tidak ada gambar, dilewati")
        continue

    # ===== COPY + RESIZE ORIGINAL =====
    resized_paths = []
    for img_path in images:
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        img = cv2.resize(img, IMG_SIZE)
        out_path = out_cls / img_path.name
        if cv2.imwrite(str(out_path), img):
            resized_paths.append(out_path)
            total_original += 1

    if not resized_paths:
        continue

    # ===== 167 HORIZONTAL FLIP =====
    for i in range(AUG_H_FLIP):
        img = cv2.imread(str(random.choice(resized_paths)))
        if img is not None:
            cv2.imwrite(str(out_cls / f"aug_hflip_{i}.jpg"), cv2.flip(img, 1))
            total_augmented += 1

    # ===== 167 VERTICAL FLIP =====
    for i in range(AUG_V_FLIP):
        img = cv2.imread(str(random.choice(resized_paths)))
        if img is not None:
            cv2.imwrite(str(out_cls / f"aug_vflip_{i}.jpg"), cv2.flip(img, 0))
            total_augmented += 1

    # ===== 166 ROTASI KOTAK (0°/90°/180°/270°) =====
    for i in range(AUG_ROTATE):
        img = cv2.imread(str(random.choice(resized_paths)))
        if img is not None:
            angle_code = random.choice(ROTATE_ANGLES)
            cv2.imwrite(str(out_cls / f"aug_rot_{i}.jpg"), cv2.rotate(img, angle_code))
            total_augmented += 1

    print(f"  {cls_dir.name}: {len(resized_paths)} original + {AUG_H_FLIP + AUG_V_FLIP + AUG_ROTATE} augmented")

elapsed = time.time() - start_time

print()
print("Preprocess BG selesai")
print(f"Total original resized : {total_original}")
print(f"Total augmented        : {total_augmented}")
print(f"Waktu proses           : {format_time(elapsed)}")
print(f"Output                 : {FINAL_BG_DIR}")
