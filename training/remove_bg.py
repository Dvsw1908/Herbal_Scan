import os
import cv2
import time
from rembg import remove

def format_time(seconds):
   minutes = int(seconds // 60)
   seconds = int(seconds % 60)
   return f"{minutes}menit {seconds}detik"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "..", "data", "raw")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "data", "nobg")

print("Mulai remove background...")
print("Input dir :", INPUT_DIR)
print("Output dir:", OUTPUT_DIR)

start_time = time.time()    
total_images = 0

os.makedirs(OUTPUT_DIR, exist_ok=True)

for class_name in os.listdir(INPUT_DIR):
    class_input_path = os.path.join(INPUT_DIR, class_name)
    class_output_path = os.path.join(OUTPUT_DIR, class_name)

    if not os.path.isdir(class_input_path):
        continue

    os.makedirs(class_output_path, exist_ok=True)

    for img_name in os.listdir(class_input_path):
        input_img_path = os.path.join(class_input_path, img_name)
        output_img_path = os.path.join(class_output_path, img_name)

        img = cv2.imread(input_img_path)
        if img is None:
            print(f"Gagal baca: {input_img_path}")
            continue

        result = remove(img)
        cv2.imwrite(output_img_path, result)
        total_images += 1

    print(f"Selesai kelas: {class_name}")

end_time = time.time()
elapsed_time = end_time - start_time
print("🎉 Remove background selesai")
print(f"🖼️ Total gambar diproses: {total_images}")
print(f"⏱️ Waktu proses: {format_time(elapsed_time)}")
