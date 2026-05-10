import os
import cv2
import time
from rembg import remove

# ============================================================
# PREPROCESSING DATA TESTING
# Step 1: Remove background  →  data/test_raw   → data/test_nobg
# Step 2: Resize 224x224     →  data/test_nobg  → data/test_final
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_DIR  = os.path.join(BASE_DIR, "..", "data", "testing")
NOBG_DIR   = os.path.join(BASE_DIR, "..", "data", "test_nobg")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "data", "test_final")

IMG_SIZE = (224, 224)
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def format_time(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes} menit {secs} detik"


def process_classes(input_dir, output_dir, process_fn, step_label):
    os.makedirs(output_dir, exist_ok=True)
    total = 0
    failed = 0

    for class_name in sorted(os.listdir(input_dir)):
        class_in  = os.path.join(input_dir, class_name)
        class_out = os.path.join(output_dir, class_name)

        if not os.path.isdir(class_in):
            continue

        os.makedirs(class_out, exist_ok=True)

        for img_name in os.listdir(class_in):
            if os.path.splitext(img_name)[1].lower() not in IMG_EXTS:
                continue

            src  = os.path.join(class_in, img_name)
            dst  = os.path.join(class_out, img_name)

            img = cv2.imread(src)
            if img is None:
                print(f"  [SKIP] Gagal baca: {src}")
                failed += 1
                continue

            result = process_fn(img)
            cv2.imwrite(dst, result)
            total += 1

        print(f"  [{step_label}] Selesai kelas: {class_name}")

    return total, failed


# ────────────────────────────────────────────────────────────
# STEP 1 — Remove Background
# ────────────────────────────────────────────────────────────
print("=" * 55)
print("STEP 1: Remove Background")
print(f"  Input : {INPUT_DIR}")
print(f"  Output: {NOBG_DIR}")
print("=" * 55)

t0 = time.time()
total1, fail1 = process_classes(INPUT_DIR, NOBG_DIR, lambda img: remove(img), "RemBG")
elapsed1 = time.time() - t0

print(f"\nSTEP 1 selesai — {total1} gambar ({fail1} gagal) | {format_time(elapsed1)}\n")

# ────────────────────────────────────────────────────────────
# STEP 2 — Resize
# ────────────────────────────────────────────────────────────
print("=" * 55)
print("STEP 2: Resize ke 224x224")
print(f"  Input : {NOBG_DIR}")
print(f"  Output: {OUTPUT_DIR}")
print("=" * 55)

t1 = time.time()
total2, fail2 = process_classes(
    NOBG_DIR, OUTPUT_DIR,
    lambda img: cv2.resize(img, IMG_SIZE),
    "Resize"
)
elapsed2 = time.time() - t1

print(f"\nSTEP 2 selesai — {total2} gambar ({fail2} gagal) | {format_time(elapsed2)}\n")

# ────────────────────────────────────────────────────────────
# SUMMARY
# ────────────────────────────────────────────────────────────
print("=" * 55)
print("SELESAI")
print(f"  Total gambar final : {total2}")
print(f"  Total waktu        : {format_time(elapsed1 + elapsed2)}")
print(f"  Output siap pakai  : {OUTPUT_DIR}")
print("=" * 55)
