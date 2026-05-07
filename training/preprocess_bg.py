"""
Preprocessing Dataset BG (Dengan Background)
- Input : data/raw  (gambar asli dengan background)
- Output: data/final bg
- Tahap 1: copy+resize original (~300) + 250 H-Flip + 250 V-Flip = 500 flip
- Tahap 2: Rotasi 500 hasil flip dengan 4 sudut (0/90/180/270) x 125 = 500 rotasi
- Total per kelas: ~300 original + 1000 augmented = ~1300
"""
import random
import time
import cv2
from pathlib import Path

# =====================
# CONFIG
# =====================
BASE_DIR     = Path(__file__).resolve().parent
RAW_DIR      = BASE_DIR.parent / "data" / "raw"
FINAL_BG_DIR = BASE_DIR.parent / "data" / "final bg"

IMG_SIZE      = (224, 224)
AUG_H_FLIP    = 250
AUG_V_FLIP    = 250
ROTATE_ANGLES = [0, 90, 180, 270]
ROT_PER_ANGLE = 125

VALID_EXTS = {".jpg", ".jpeg", ".png"}

FINAL_BG_DIR.mkdir(parents=True, exist_ok=True)


def rotate_image(img, angle: int):
    if angle == 0:
        return img.copy()
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REFLECT)


def format_time(seconds: float) -> str:
    return f"{int(seconds // 60)} menit {int(seconds % 60)} detik"


print("Preprocess BG dimulai")
print(f"Input  : {RAW_DIR}")
print(f"Output : {FINAL_BG_DIR}")
print(f"Tahap 1 — H-Flip: {AUG_H_FLIP} | V-Flip: {AUG_V_FLIP} = {AUG_H_FLIP + AUG_V_FLIP} flip")
print(f"Tahap 2 — Rotasi {ROTATE_ANGLES} x {ROT_PER_ANGLE} = {len(ROTATE_ANGLES) * ROT_PER_ANGLE} rotasi")

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

    # ===== TAHAP 1: FLIP dari original =====
    flipped_paths = []

    for i in range(AUG_H_FLIP):
        img = cv2.imread(str(random.choice(resized_paths)))
        if img is not None:
            out_path = out_cls / f"aug_hflip_{i}.jpg"
            cv2.imwrite(str(out_path), cv2.flip(img, 1))
            flipped_paths.append(out_path)
            total_augmented += 1

    for i in range(AUG_V_FLIP):
        img = cv2.imread(str(random.choice(resized_paths)))
        if img is not None:
            out_path = out_cls / f"aug_vflip_{i}.jpg"
            cv2.imwrite(str(out_path), cv2.flip(img, 0))
            flipped_paths.append(out_path)
            total_augmented += 1

    # ===== TAHAP 2: ROTASI dari hasil flip =====
    rot_idx = 0
    for angle in ROTATE_ANGLES:
        for i in range(ROT_PER_ANGLE):
            img = cv2.imread(str(random.choice(flipped_paths)))
            if img is not None:
                out_path = out_cls / f"aug_rot{angle}_{rot_idx}.jpg"
                cv2.imwrite(str(out_path), rotate_image(img, angle))
                rot_idx += 1
                total_augmented += 1

    flip_total = AUG_H_FLIP + AUG_V_FLIP
    rot_total  = len(ROTATE_ANGLES) * ROT_PER_ANGLE
    print(f"  {cls_dir.name}: {len(resized_paths)} original + {flip_total} flip + {rot_total} rotasi")

elapsed = time.time() - start_time

print()
print("Preprocess BG selesai")
print(f"Total original resized : {total_original}")
print(f"Total augmented        : {total_augmented}")
print(f"Waktu proses           : {format_time(elapsed)}")
print(f"Output                 : {FINAL_BG_DIR}")
