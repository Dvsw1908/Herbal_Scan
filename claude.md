# Instruksi Arsitektur & Best Practice untuk Claude Code

Halo Claude Code, 

Kamu bertindak sebagai developer/arsitek untuk melakukan pembaruan di repository ini. Pengguna (User) memiliki 3 permintaan pembaruan kode. Silakan kerjakan tugas-tugas di bawah ini dengan menerapkan prinsip best practice.

## Tugas 1: Penyesuaian Pipeline Training (`training/train_model.py`)
**Masalah saat ini**: Script saat ini sengaja membuang kelas "Rusak" (seperti terlihat pada fungsi `load_species_only`).
**Arahan**:
1. Ubah logika pada `training/train_model.py` agar **tidak membuang** data atau kelas apapun.
2. Biarkan model menganalisa semua variasi data yang ada di dataset: daun sehat, daun rusak, gambar dengan background (bg), maupun tanpa background (no bg).
3. Hal ini sangat penting karena pada saat testing nanti, model akan diuji untuk mengidentifikasi berbagai kondisi daun tersebut (kondisi riil). Pastikan pipeline dataset loading menangani semua kelas ini dengan benar tanpa ada yang di-_exclude_.

## Tugas 2: Visualisasi Akurasi (`training/main.ipynb`)
**Masalah saat ini**: Pada plot hasil evaluasi akurasi, grafik langsung terlihat tinggi dari awal sehingga tidak menggambarkan proses pembelajaran model (lonjakan) dari awal.
**Arahan**:
1. Modifikasi cara visualisasi/plotting metrik akurasi di dalam file `training/main.ipynb`.
2. Pastikan grafik akurasi divisualisasikan sedemikian rupa sehingga dimulai dari 0 (atau setara dengan epoch awal/sebelum training) agar terlihat lonjakan kurva pembelajarannya secara detail dan bertahap.
3. Kamu bisa menambahkan point `0` pada awal array history atau memastikan sumbu Y (Y-axis) atau step loggignya direpresentasikan dengan baik.

## Tugas 3: Penambahan Variabel Data Tanaman (`herbal_leaf_app/lib/data/plant_data.dart`)
**Masalah saat ini**: User ingin menampilkan gambar spesifik daun dan kegunaannya pada aplikasi, namun properti tersebut belum terdefinisi dengan jelas di model data.
**Arahan**:
1. Buka file `herbal_leaf_app/lib/models/herbal_plant.dart` dan tambahkan variabel baru pada class `HerbalPlant`, misalnya:
   - `leafImagePath` (tipe `String`) untuk menyimpan path gambar daun.
   - `usage` / `kegunaan` (tipe `String` atau `List<String>`) untuk menyimpan informasi detail terkait kegunaan daun tersebut.
2. Buka file `herbal_leaf_app/lib/data/plant_data.dart` lalu lengkapi inisialisasi variabel di dalam `kHerbalPlants` dengan data yang sesuai (gunakan *placeholder image path* jika perlu, misal `assets/images/placeholder_leaf.png`, dan tulis deskripsi kegunaan sementara yang logis untuk setiap tanaman).
3. Pastikan kamu mempertahankan null-safety dan konsistensi tipe data bawaan Dart.

---
**Catatan Best Practice**:
- Pastikan kamu membaca kode *existing* sebelum merubahnya.
- Jangan mengubah arsitektur kode secara drastis jika tidak berhubungan dengan 3 poin di atas.
- Pastikan kode Flutter tetap bisa di-compile dan kode Python tetap berjalan tanpa error.
