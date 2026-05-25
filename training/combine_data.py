# import torch
# import torch.nn as nn
# from torchvision import models, transforms
# from PIL import Image
# import pandas as pd
# from pathlib import Path

# # ===== KONFIGURASI =====
# MODEL_PATH   = Path("model/shufflenet_exp2_80.pth")  # sesuaikan path model
# TEST_DIR     = Path("data/train_combined")                   # sesuaikan path folder gambar testing
# OUTPUT_CSV   = Path("hasil_prediksi.csv")

# CLASS_NAMES = [
#     "Daun Alpukat BG", "Daun Alpukat NoBG",
#     "Daun Alpukat Rusak BG", "Daun Alpukat Rusak NoBG",
#     "Daun Belimbing Wuluh BG", "Daun Belimbing Wuluh NoBG",
#     "Daun Belimbing Wuluh Rusak BG", "Daun Belimbing Wuluh Rusak NoBG",
#     "Daun Jambu Biji Rusak BG", "Daun Jambu Biji Rusak NoBG",
#     "Daun Jambu biji BG", "Daun Jambu biji NoBG",
#     "Daun Leci BG", "Daun Leci NoBG",
#     "Daun Leci Rusak BG", "Daun Leci Rusak NoBG",
#     "Daun Nangka BG", "Daun Nangka NoBG",
#     "Daun Nangka Rusak BG", "Daun Nangka Rusak NoBG",
#     "Daun Salam BG", "Daun Salam NoBG",
#     "Daun Salam Rusak BG", "Daun Salam Rusak NoBG",
#     "Daun Sirsak BG", "Daun Sirsak NoBG",
#     "Daun Sirsak Rusak BG", "Daun Sirsak Rusak NoBG",
#     "Daun Srikaya BG", "Daun Srikaya NoBG",
#     "Daun Srikaya Rusak BG", "Daun Srikaya Rusak NoBG",
# ]

# # ===== LOAD MODEL =====
# net = models.shufflenet_v2_x1_0(weights=None)
# net.fc = nn.Linear(net.fc.in_features, len(CLASS_NAMES))
# state = torch.load(MODEL_PATH, map_location="cpu", weights_only=True)
# net.load_state_dict(state)
# net.eval()

# # ===== TRANSFORM =====
# transform = transforms.Compose([
#     transforms.Resize((224, 224)),
#     transforms.ToTensor(),
#     transforms.Normalize([0.485, 0.456, 0.406],
#                          [0.229, 0.224, 0.225]),
# ])

# # ===== PREDIKSI =====
# results = []
# image_paths = sorted(TEST_DIR.glob("**/*.jpg")) + sorted(TEST_DIR.glob("**/*.png"))

# print(f"Ditemukan {len(image_paths)} gambar...")

# for img_path in image_paths:
#     img = Image.open(img_path).convert("RGB")
#     tensor = transform(img).unsqueeze(0)

#     with torch.no_grad():
#         output = net(tensor)
#         probs = torch.softmax(output, dim=1)
#         conf, pred_idx = torch.max(probs, dim=1)

#     results.append({
#         "No": len(results) + 1,
#         "Nama File": img_path.name,
#         "Kelas Daun": img_path.parent.name,  # nama folder = nama kelas
#         "Prediksi Kelas Daun": CLASS_NAMES[pred_idx.item()],
#         "Confidence Score": f"{conf.item() * 100:.2f}%",
#     })

# # ===== SIMPAN CSV =====
# df = pd.DataFrame(results)
# df.to_csv(OUTPUT_CSV, index=False)
# print(f"Selesai! Hasil disimpan di: {OUTPUT_CSV}")

"""
csv_to_docx.py
Membuat tabel Word (Lampiran) dari hasil prediksi CSV + folder gambar.

Cara pakai:
  python csv_to_docx.py

Sesuaikan tiga variabel di bagian KONFIGURASI di bawah.
"""

import csv
import json
import subprocess
import sys
from pathlib import Path

# ==================== KONFIGURASI ====================
CSV_PATH    = Path("C:\\Users\\dvsw1\\Documents\\Kuliah\\Kuliah\\Skripsi\\Code\\hasil_prediksi.csv")   # path file CSV hasil prediksi
IMAGE_DIR   = Path("data/train_combined")  # folder root gambar (cari rekursif)
OUTPUT_DOCX = Path("Lampiran_Hasil_Testing.docx")
JUDUL       = "Lampiran 7 Hasil Data Testing Seluruh Kelas"
# =====================================================

# --- Baca CSV ---
rows = []
with open(CSV_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

print(f"Jumlah data: {len(rows)}")

# --- Cari path gambar (rekursif) ---
img_index = {}
for ext in ("*.jpg", "*.jpeg", "*.png"):
    for p in IMAGE_DIR.rglob(ext):
        img_index[p.name.lower()] = p

# --- Bangun data untuk JS ---
table_data = []
for row in rows:
    nama_file = row.get("Nama File", "").strip()
    img_path  = img_index.get(nama_file.lower())
    table_data.append({
        "no":        row.get("No", ""),
        "kelas":     row.get("Kelas Daun", ""),
        "prediksi":  row.get("Prediksi Kelas Daun", ""),
        "confidence":row.get("Confidence Score", ""),
        "img_path":  str(img_path) if img_path else "",
        "img_name":  nama_file,
    })

# --- Tulis script JS sementara ---
js_data = json.dumps(table_data, ensure_ascii=False)

js_code = r"""
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, AlignmentType, BorderStyle, WidthType, ShadingType,
  VerticalAlign, HeadingLevel
} = require('docx');
const fs   = require('fs');
const path = require('path');

const tableData = """ + js_data + r""";
const OUTPUT    = """ + json.dumps(str(OUTPUT_DOCX)) + r""";

const border = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
const borders = { top: border, bottom: border, left: border, right: border };

const cellOpts = (w) => ({
  borders,
  width: { size: w, type: WidthType.DXA },
  margins: { top: 80, bottom: 80, left: 120, right: 120 },
  verticalAlign: VerticalAlign.CENTER,
});

// Lebar kolom (total ~9360 DXA untuk A4 margin 1 inch)
const COL = [600, 2200, 2000, 2500, 2060]; // No | Gambar | Kelas | Prediksi | Confidence

function headerCell(text, w) {
  return new TableCell({
    ...cellOpts(w),
    shading: { fill: "1F3864", type: ShadingType.CLEAR },
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text, bold: true, color: "FFFFFF", size: 20 })]
    })]
  });
}

function textCell(text, w, center = true) {
  return new TableCell({
    ...cellOpts(w),
    children: [new Paragraph({
      alignment: center ? AlignmentType.CENTER : AlignmentType.LEFT,
      children: [new TextRun({ text: String(text), size: 18 })]
    })]
  });
}

function imageCell(imgPath, w) {
  if (!imgPath || !fs.existsSync(imgPath)) {
    return textCell("-", w);
  }
  const ext  = path.extname(imgPath).toLowerCase().replace(".", "");
  const type = ext === "jpg" ? "jpg" : ext === "jpeg" ? "jpg" : "png";
  const data = fs.readFileSync(imgPath);
  return new TableCell({
    ...cellOpts(w),
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new ImageRun({
        data,
        type,
        transformation: { width: 80, height: 60 }
      })]
    })]
  });
}

// Header row
const headerRow = new TableRow({
  tableHeader: true,
  children: [
    headerCell("No", COL[0]),
    headerCell("Gambar Testing", COL[1]),
    headerCell("Kelas Daun", COL[2]),
    headerCell("Prediksi Kelas Daun", COL[3]),
    headerCell("Confidence Score", COL[4]),
  ]
});

// Data rows
const dataRows = tableData.map(d => new TableRow({
  children: [
    textCell(d.no,         COL[0]),
    imageCell(d.img_path,  COL[1]),
    textCell(d.kelas,      COL[2], false),
    textCell(d.prediksi,   COL[3], false),
    textCell(d.confidence, COL[4]),
  ]
}));

const table = new Table({
  width: { size: COL.reduce((a,b)=>a+b,0), type: WidthType.DXA },
  columnWidths: COL,
  rows: [headerRow, ...dataRows],
});

const doc = new Document({
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 200 },
        children: [new TextRun({ text: """ + json.dumps(JUDUL) + r""", bold: true, size: 24 })]
      }),
      table,
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUTPUT, buf);
  console.log("Selesai:", OUTPUT);
});
"""

js_file = Path("make_lampiran.js")
js_file.write_text(js_code, encoding="utf-8")

# --- Jalankan JS ---
result = subprocess.run(["node", str(js_file)], capture_output=True, text=True)
if result.returncode != 0:
    print("ERROR:", result.stderr)
    sys.exit(1)
print(result.stdout)
print(f"File Word tersimpan: {OUTPUT_DOCX.resolve()}")