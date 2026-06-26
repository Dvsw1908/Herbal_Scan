# 🌿 HerbalScan — Klasifikasi Daun Herbal Berbasis ShuffleNetV2

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Platform](https://img.shields.io/badge/Platform-Android%20%7C%20Backend-blue)
![Language](https://img.shields.io/badge/Language-Python%20%7C%20Dart-yellow)
![Framework](https://img.shields.io/badge/Framework-Flutter%20%7C%20FastAPI%20%7C%20PyTorch-cyan)

**HerbalScan** adalah aplikasi klasifikasi citra daun herbal. Pengguna memotret/memilih
gambar daun, lalu model **ShuffleNetV2** memprediksi spesiesnya beserta tingkat keyakinan
(confidence) dan 3 prediksi teratas. Proyek ini merupakan bagian dari skripsi dan terdiri
dari tiga komponen: **pelatihan model (Python)**, **backend inferensi (FastAPI)**, dan
**aplikasi mobile (Flutter/Android)**.

**8 spesies daun** yang dikenali model: Alpukat, Belimbing Wuluh, Jambu Biji, Leci, Nangka,
Salam, Sirsak, Srikaya — masing-masing dalam kondisi *sehat/rusak* dan latar *BG/NoBG*
(16 kelas untuk Eksperimen 1 = sehat saja, 32 kelas untuk Eksperimen 2 = semua kondisi).

---

## 📑 Daftar Isi
- [1. Program Siap Pakai (Artefak)](#1-program-siap-pakai-artefak)
- [2. Instalasi](#2-instalasi)
- [3. Listing Program](#3-listing-program)
- [4. Manual Pemakaian](#4-manual-pemakaian)
- [5. Catatan & Troubleshooting](#5-catatan--troubleshooting)

---

## 1. Program Siap Pakai (Artefak)

Sesuai platform, program sudah tersedia dalam bentuk berikut:

| Platform | Bentuk | Lokasi / Cara jalan |
|---|---|---|
| **Android** | **`.apk` (siap install)** | `herbal_leaf_app/build/app/outputs/flutter-apk/app-release.apk` (±265 MB) |
| **Backend** | **Script Python (server)** | `backend/app.py` dijalankan via `uvicorn` (lihat [§2](#2-instalasi)) |
| **Model (server)** | Bobot PyTorch `.pth` | `model/Hasil 1..4/shufflenet_{exp}_{split}.pth` |
| **Model (on-device)** | TorchScript mobile `.ptl` | `herbal_leaf_app/assets/model/shufflenet_exp2.ptl` + `labels.txt` |
| **Pelatihan/Evaluasi** | Notebook & script | `training/main.ipynb`, `training/eval_testset.py` |

> Cara tercepat mencoba: **install `app-release.apk` di HP Android**, lalu jalankan backend
> di PC dan arahkan aplikasi ke alamat IP backend (lihat [§4](#4-manual-pemakaian)).

---

## 2. Instalasi

### 2.1 Prasyarat
- **Python 3.11** (proyek diuji pada 3.11.0)
- **Flutter SDK** (Dart SDK `^3.11.5`) + Android Studio / Android SDK — hanya bila ingin
  build ulang atau menjalankan aplikasi dari source
- **Git**
- Perangkat **Android** atau emulator untuk menjalankan aplikasi

### 2.2 Backend & Pelatihan (Python)

```bash
# 1. Buat & aktifkan virtual environment
python -m venv venv
venv\Scripts\activate            # Windows (PowerShell: .\venv\Scripts\Activate.ps1)
# source venv/bin/activate       # Linux / macOS

# 2. Pasang dependency
pip install -r requirements.txt
```

**Langkah penting — siapkan bobot model untuk backend.**
Backend memuat `model/shufflenet_exp2_70.pth`, sedangkan bobot tersimpan di subfolder run.
Salin salah satu run (disarankan `Hasil 4`, hasil terbaik) ke folder `model/`:

```bash
# Windows (PowerShell)
Copy-Item "model/Hasil 4/shufflenet_exp2_70.pth" "model/"

# Linux / macOS / Git Bash
cp "model/Hasil 4/shufflenet_exp2_70.pth" model/
```

Jalankan server:

```bash
cd backend
uvicorn app:app --host 0.0.0.0 --port 8000
# Cek di browser: http://localhost:8000  -> {"status":"HerbalScan backend siap"}
# Dokumentasi API interaktif: http://localhost:8000/docs
```

### 2.3 Aplikasi Mobile (Flutter)

Jika hanya ingin memakai: **cukup install `app-release.apk`** (lihat [§1](#1-program-siap-pakai-artefak)).
Untuk menjalankan dari source / build ulang:

```bash
cd herbal_leaf_app
flutter pub get
flutter run                       # jalankan ke emulator/device yang terhubung
flutter build apk --release       # menghasilkan app-release.apk
```

---

## 3. Listing Program

### 3.1 Struktur Repositori

```text
Code/
├── backend/                     # Server inferensi FastAPI
│   ├── app.py                   # Endpoint API (/predict, /history)
│   ├── inference.py             # Muat ShuffleNetV2 + praproses + prediksi
│   ├── database.py              # Penyimpanan riwayat (SQLite)
│   └── predictions.db           # Basis data riwayat prediksi
│
├── herbal_leaf_app/             # Aplikasi Flutter (Android/iOS/Web/Desktop)
│   ├── lib/                     # Kode sumber Dart (UI, logic, data)
│   │   ├── main.dart
│   │   ├── pages/               # Halaman UI (home, result, history, dll.)
│   │   ├── services/            # api_service.dart (koneksi ke backend)
│   │   ├── providers/ repositories/ models/ widgets/ data/
│   ├── assets/model/            # Model on-device (.ptl) + labels.txt
│   └── build/.../app-release.apk# APK siap pakai
│
├── training/                    # Pelatihan & evaluasi model
│   ├── main.ipynb               # Notebook utama pelatihan + evaluasi
│   ├── train_model.py           # Pipeline pelatihan (versi script)
│   ├── eval_testset.py          # Evaluasi pada data uji independen (data/test)
│   ├── export_model.py          # Export .pth -> TorchScript mobile (.ptl)
│   └── *.py                      # Skrip praproses dataset (lihat tabel di bawah)
│
├── model/                       # Bobot terlatih per run
│   └── Hasil 1..4/shufflenet_{exp1|exp2}_{70|80}.pth
├── results/                     # Metrik & grafik per run
│   └── Hasil 1..4/results_*.json, plot_*.png, cm_*.png
├── data/                        # Dataset (raw, resized, final, test, dll.)
│
├── requirements.txt             # Dependency Python
├── Manual_Book_HerbalScan.docx  # Manual book (dokumen)
└── README.md                    # Dokumen ini
```

### 3.2 Skrip Pelatihan & Utilitas (`training/`)

| Berkas | Fungsi |
|---|---|
| `main.ipynb` | Notebook pelatihan ShuffleNetV2: Eksperimen 1 (sehat) & 2 (semua kondisi), split 70:30 & 80:20, menghasilkan model + grafik + metrik. |
| `train_model.py` | Versi script dari pipeline pelatihan di notebook. |
| `eval_testset.py` | Evaluasi bobot pada **data uji independen** `data/test`; bandingkan metrik **Validasi vs Test** + selisih (indikator overfitting). Default: run `Hasil 4`. |
| `export_model.py` | Konversi `.pth` → TorchScript mobile `.ptl` untuk dipakai aplikasi. |
| `build_final_dataset.py`, `combine_data.py` | Menyusun dataset final (gabungan BG + NoBG). |
| `augment.py`, `resize.py` | Augmentasi & penyeragaman ukuran citra (224×224). |
| `remove_bg.py`, `preprocess_bg.py`, `preprocess_test.py` | Penghapusan/penanganan latar (rembg) untuk varian NoBG & data uji. |
| `test.py`, `fix_prediksi_csv.py`, `make_lampiran.js` | Utilitas pengujian & pembuatan lampiran hasil. |

### 3.3 Endpoint Backend (`backend/app.py`)

| Method | Endpoint | Keterangan |
|---|---|---|
| `GET` | `/` | Cek status server. |
| `POST` | `/predict` | Upload gambar (JPEG/PNG/WEBP, maks 10 MB) → kelas prediksi, confidence, top-3. |
| `GET` | `/history` | Daftar riwayat prediksi. |
| `DELETE` | `/history/{id}` | Hapus satu entri riwayat. |

---

## 4. Manual Pemakaian

### 4.1 Menjalankan via Aplikasi (alur utama)

1. **Jalankan backend** di PC (lihat [§2.2](#22-backend--pelatihan-python)). Pastikan tampil
   status `HerbalScan backend siap`.
2. **Atur alamat backend** di aplikasi (`herbal_leaf_app/lib/services/api_service.dart`,
   `baseUrl`):
   - **Emulator Android**: `http://10.0.2.2:8000` (default, menunjuk ke localhost PC).
   - **HP fisik (satu jaringan Wi-Fi)**: ganti ke IP LAN PC, mis. `http://192.168.1.10:8000`,
     lalu build ulang APK (`flutter build apk --release`).
3. **Install & buka aplikasi** (`app-release.apk`).
4. Di **Beranda**: pilih **ambil foto** atau **pilih dari galeri** daun yang ingin diperiksa.
5. Tekan **Prediksi**. Aplikasi mengirim gambar ke backend dan menampilkan:
   - Nama spesies hasil prediksi
   - **Confidence** (tingkat keyakinan)
   - **Top-3** kemungkinan kelas
   - Detail tanaman pada halaman **Plant Detail**.
6. Hasil otomatis tersimpan di **Riwayat (History)** — bisa dibuka ulang atau dihapus.
   Tersedia juga halaman **Settings** dan mode **batch** untuk beberapa gambar.

### 4.2 Menjalankan Evaluasi Model (untuk laporan skripsi)

```bash
# Evaluasi run Hasil 4 (default) pada data uji independen data/test
python training/eval_testset.py

# Run tertentu / semua run
python training/eval_testset.py "Hasil 1"
python training/eval_testset.py all
```

Output (per run, di `results/Hasil N/`):
- Ringkasan **Validasi vs Test** + selisih akurasi (overfitting) di terminal
- `cm_test_{tag}.png` — confusion matrix data uji
- `results_test_{tag}.json` — metrik lengkap (accuracy, precision, recall, F1, report)

> **Penting:** angka ~100% dari notebook adalah **akurasi validasi** (split dari data latih,
> optimistis). Angka yang sah untuk **Bab Pengujian** adalah hasil `eval_testset.py` pada
> `data/test` (uji independen).

### 4.3 Melatih Ulang / Export Model

```bash
# Latih ulang (via notebook): buka training/main.ipynb, pilih kernel venv, Run All
# atau jalankan versi script:
python training/train_model.py

# Export model terlatih ke format mobile (.ptl) untuk aplikasi
python training/export_model.py
```

---

## 5. Catatan & Troubleshooting

- **Backend gagal memuat model / `FileNotFoundError`** → pastikan langkah penyalinan bobot
  di [§2.2](#22-backend--pelatihan-python) sudah dilakukan (`model/shufflenet_exp2_70.pth`
  harus ada di folder `model/`).
- **Aplikasi tak bisa terhubung ke backend** → cek `baseUrl` di `api_service.dart`, pastikan
  PC & HP satu jaringan, dan firewall mengizinkan port `8000`.
- **`venv` tidak terdeteksi di VSCode/Jupyter** → pilih interpreter `./venv/Scripts/python.exe`
  via `Python: Select Interpreter`, lalu pilih kernel yang sama di notebook.
- **GPU**: `torch` pada `requirements.txt` adalah versi CPU. Untuk GPU, pasang torch varian
  CUDA yang sesuai. Pelatihan/inferensi tetap berjalan di CPU bila tanpa GPU.
- **Spesies di luar 8 kelas** (mis. *Mangga*) tidak dikenali model dan memang dilewati saat
  evaluasi.

---

> Dikembangkan sebagai bagian dari skripsi klasifikasi daun herbal menggunakan ShuffleNetV2.
> Manual lengkap tersedia pada `Manual_Book_HerbalScan.docx`.
