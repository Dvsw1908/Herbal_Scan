"""
csv_to_docx.py
Membuat tabel Word (Lampiran) dari hasil prediksi CSV + folder gambar.

Cara pakai:
  python csv_to_docx.py

Sesuaikan variabel di bagian KONFIGURASI di bawah.
"""

import csv
import json
import subprocess
import sys
from pathlib import Path

# ==================== KONFIGURASI ====================
CSV_PATH    = Path("hasil_prediksi.csv")
IMAGE_DIR   = Path("data/train_combined")
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

# --- Bangun data untuk JS ---
table_data = []
for row in rows:
    nama_file = row.get("Nama File", "").strip()
    kelas     = row.get("Kelas Daun", "").strip()
    img_path  = IMAGE_DIR / kelas / nama_file

    if not img_path.exists():
        found = list(IMAGE_DIR.rglob(nama_file))
        img_path = found[0] if found else Path("")

    table_data.append({
        "no":        row.get("No", ""),
        "kelas":     kelas,
        "prediksi":  row.get("Prediksi Kelas Daun", ""),
        "confidence":row.get("Confidence Score", ""),
        "img_path":  str(img_path).replace("\\", "/") if img_path.exists() else "",
        "img_name":  nama_file,
    })

missing = sum(1 for d in table_data if not d["img_path"])
print(f"Gambar tidak ditemukan: {missing}/{len(table_data)}")

# --- Tulis script JS sementara ---
js_data = json.dumps(table_data, ensure_ascii=False)

js_code = """
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, AlignmentType, BorderStyle, WidthType, ShadingType, VerticalAlign
} = require('docx');
const fs   = require('fs');
const path = require('path');

const tableData = """ + js_data + """;
const OUTPUT    = """ + json.dumps(str(OUTPUT_DOCX).replace("\\", "/")) + """;

const border  = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
const borders = { top: border, bottom: border, left: border, right: border };

const COL = [500, 2200, 2100, 2500, 2060];

function cellOpts(w) {
  return {
    borders,
    width: { size: w, type: WidthType.DXA },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    verticalAlign: VerticalAlign.CENTER,
  };
}

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

function textCell(text, w, center) {
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
    return textCell("-", w, true);
  }
  try {
    const ext  = path.extname(imgPath).toLowerCase().replace(".", "");
    const type = (ext === "jpg" || ext === "jpeg") ? "jpg" : "png";
    const data = fs.readFileSync(imgPath);
    return new TableCell({
      ...cellOpts(w),
      children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new ImageRun({ data, type, transformation: { width: 80, height: 60 } })]
      })]
    });
  } catch(e) {
    console.error("Gagal baca gambar:", imgPath, e.message);
    return textCell("-", w, true);
  }
}

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

const dataRows = tableData.map(d => new TableRow({
  children: [
    textCell(d.no,         COL[0], true),
    imageCell(d.img_path,  COL[1]),
    textCell(d.kelas,      COL[2], false),
    textCell(d.prediksi,   COL[3], false),
    textCell(d.confidence, COL[4], true),
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
        children: [new TextRun({ text: """ + json.dumps(JUDUL) + """, bold: true, size: 24 })]
      }),
      table,
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUTPUT, buf);
  console.log("Selesai:", OUTPUT);
}).catch(err => {
  console.error("ERROR:", err);
  process.exit(1);
});
"""

js_file = Path("make_lampiran.js")
js_file.write_text(js_code, encoding="utf-8")

# --- Jalankan JS ---
result = subprocess.run(["node", str(js_file)], capture_output=True, text=True)
if result.returncode != 0:
    print("ERROR JS:")
    print(result.stderr)
    sys.exit(1)

print(result.stdout.strip())
print(f"File Word tersimpan: {OUTPUT_DOCX.resolve()}")

# Hapus file JS sementara
js_file.unlink(missing_ok=True)