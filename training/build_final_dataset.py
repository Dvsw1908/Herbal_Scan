import os
import shutil
import time

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes} menit {seconds} detik"

# ===== PATH AMAN =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RESIZED_DIR = os.path.join(BASE_DIR, "..", "data", "resized")
AUGMENTED_DIR = os.path.join(BASE_DIR, "..", "data", "augmented")
FINAL_DIR = os.path.join(BASE_DIR, "..", "data", "final")

print("🚀 Mulai build dataset FINAL")
print("Resized   :", RESIZED_DIR)
print("Augmented :", AUGMENTED_DIR)
print("Final     :", FINAL_DIR)

start_time = time.time()
total_images = 0

os.makedirs(FINAL_DIR, exist_ok=True)

def copy_dataset(src_dir, dst_dir):
    global total_images

    for class_name in os.listdir(src_dir):
        src_class = os.path.join(src_dir, class_name)
        dst_class = os.path.join(dst_dir, class_name)

        if not os.path.isdir(src_class):
            continue

        os.makedirs(dst_class, exist_ok=True)

        for img_name in os.listdir(src_class):
            src_img = os.path.join(src_class, img_name)
            dst_img = os.path.join(dst_class, img_name)

            if not os.path.isfile(src_img):
                continue

            shutil.copy(src_img, dst_img)
            total_images += 1

# Copy data asli (resized)
copy_dataset(RESIZED_DIR, FINAL_DIR)

# Copy data augmentasi
copy_dataset(AUGMENTED_DIR, FINAL_DIR)

end_time = time.time()
elapsed_time = end_time - start_time

print("🎉 Dataset FINAL selesai dibuat")
print(f"🖼️ Total gambar di FINAL: {total_images}")
print(f"⏱️ Waktu proses: {format_time(elapsed_time)}")