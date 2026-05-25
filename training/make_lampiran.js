const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  Table,
  TableRow,
  TableCell,
  ImageRun,
  AlignmentType,
  BorderStyle,
  WidthType,
  ShadingType,
  VerticalAlign,
} = require("docx");
const fs = require("fs");
const path = require("path");

const ROOT_DIR = path.resolve(__dirname, "..");
const DEFAULT_CSV_PATH = path.join(ROOT_DIR, "hasil_prediksi.csv");
const FALLBACK_CSV_PATH = path.join(ROOT_DIR, "hasil_prediksi_baru.csv");
const CSV_PATH = process.env.CSV_PATH
  ? path.resolve(process.env.CSV_PATH)
  : chooseCsvPath();
const IMAGE_DIR = path.join(ROOT_DIR, "data", "train_combined");
const OUTPUT_DOCX = path.join(ROOT_DIR, "Lampiran_Hasil_Testing.docx");
const TITLE = "Lampiran 7 Hasil Data Testing Seluruh Kelas";
const CSV_COLUMNS = [
  "No",
  "Nama File",
  "Kelas Daun",
  "Prediksi Kelas Daun",
  "Confidence Score",
];

function chooseCsvPath() {
  if (!fs.existsSync(FALLBACK_CSV_PATH)) return DEFAULT_CSV_PATH;
  if (!fs.existsSync(DEFAULT_CSV_PATH)) return FALLBACK_CSV_PATH;

  const fallbackTime = fs.statSync(FALLBACK_CSV_PATH).mtimeMs;
  const defaultTime = fs.statSync(DEFAULT_CSV_PATH).mtimeMs;
  return fallbackTime >= defaultTime ? FALLBACK_CSV_PATH : DEFAULT_CSV_PATH;
}

function parseCsvLine(line) {
  const values = [];
  let current = "";
  let quoted = false;

  for (let i = 0; i < line.length; i += 1) {
    const char = line[i];
    const next = line[i + 1];
    if (char === '"' && quoted && next === '"') {
      current += '"';
      i += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (char === "," && !quoted) {
      values.push(current);
      current = "";
    } else {
      current += char;
    }
  }

  values.push(current);
  return values.map((value) => value.trim());
}

function readPredictionCsv(csvPath) {
  const lines = fs
    .readFileSync(csvPath, "utf8")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);

  const headerIndex = lines.findIndex((line) => {
    const cells = parseCsvLine(line);
    return CSV_COLUMNS.every((column, index) => cells[index] === column);
  });

  if (headerIndex === -1) {
    throw new Error(`Header CSV tidak ditemukan di ${csvPath}`);
  }

  const headers = parseCsvLine(lines[headerIndex]);
  return lines.slice(headerIndex + 1).map((line) => {
    const cells = parseCsvLine(line);
    return Object.fromEntries(headers.map((header, index) => [header, cells[index] || ""]));
  });
}

function normalizeKey(value) {
  return String(value).trim().toLowerCase();
}

function buildClassDirIndex(rootDir) {
  return Object.fromEntries(
    fs
      .readdirSync(rootDir, { withFileTypes: true })
      .filter((entry) => entry.isDirectory())
      .map((entry) => [normalizeKey(entry.name), path.join(rootDir, entry.name)])
  );
}

function findImagePath(row, classDirIndex) {
  const actualClass = row["Kelas Daun"] || "";
  const fileName = row["Nama File"] || "";
  const classDir = classDirIndex[normalizeKey(actualClass)];

  if (classDir) {
    const exactPath = path.join(classDir, fileName);
    if (fs.existsSync(exactPath)) return exactPath;
  }

  const matches = [];
  for (const dir of Object.values(classDirIndex)) {
    const candidate = path.join(dir, fileName);
    if (fs.existsSync(candidate)) matches.push(candidate);
  }

  return matches[0] || "";
}

function makeTableData() {
  const rows = readPredictionCsv(CSV_PATH);
  const classDirIndex = buildClassDirIndex(IMAGE_DIR);

  return rows.map((row, index) => ({
    no: row["No"] || String(index + 1),
    kelas: row["Kelas Daun"] || "",
    prediksi: row["Prediksi Kelas Daun"] || "",
    confidence: row["Confidence Score"] || "",
    imgPath: findImagePath(row, classDirIndex),
    imgName: row["Nama File"] || "",
  }));
}

const border = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
const borders = { top: border, bottom: border, left: border, right: border };
const COL = [600, 2200, 2000, 2500, 2060];

function cellOpts(width) {
  return {
    borders,
    width: { size: width, type: WidthType.DXA },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    verticalAlign: VerticalAlign.CENTER,
  };
}

function headerCell(text, width) {
  return new TableCell({
    ...cellOpts(width),
    shading: { fill: "1F3864", type: ShadingType.CLEAR },
    children: [
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text, bold: true, color: "FFFFFF", size: 20 })],
      }),
    ],
  });
}

function textCell(text, width, center = true) {
  return new TableCell({
    ...cellOpts(width),
    children: [
      new Paragraph({
        alignment: center ? AlignmentType.CENTER : AlignmentType.LEFT,
        children: [new TextRun({ text: String(text), size: 18 })],
      }),
    ],
  });
}

function imageCell(imgPath, width) {
  if (!imgPath || !fs.existsSync(imgPath)) {
    return textCell("-", width);
  }

  const extension = path.extname(imgPath).toLowerCase();
  const type = extension === ".jpg" || extension === ".jpeg" ? "jpg" : "png";
  const data = fs.readFileSync(imgPath);

  return new TableCell({
    ...cellOpts(width),
    children: [
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new ImageRun({
            data,
            type,
            transformation: { width: 80, height: 60 },
          }),
        ],
      }),
    ],
  });
}

function buildDocument(tableData) {
  const headerRow = new TableRow({
    tableHeader: true,
    children: [
      headerCell("No", COL[0]),
      headerCell("Gambar Testing", COL[1]),
      headerCell("Kelas Daun", COL[2]),
      headerCell("Prediksi Kelas Daun", COL[3]),
      headerCell("Confidence Score", COL[4]),
    ],
  });

  const dataRows = tableData.map(
    (item) =>
      new TableRow({
        children: [
          textCell(item.no, COL[0]),
          imageCell(item.imgPath, COL[1]),
          textCell(item.kelas, COL[2], false),
          textCell(item.prediksi, COL[3], false),
          textCell(item.confidence, COL[4]),
        ],
      })
  );

  return new Document({
    sections: [
      {
        properties: {
          page: {
            size: { width: 11906, height: 16838 },
            margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
          },
        },
        children: [
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 200 },
            children: [new TextRun({ text: TITLE, bold: true, size: 24 })],
          }),
          new Table({
            width: { size: COL.reduce((total, width) => total + width, 0), type: WidthType.DXA },
            columnWidths: COL,
            rows: [headerRow, ...dataRows],
          }),
        ],
      },
    ],
  });
}

async function main() {
  const tableData = makeTableData();
  const missingImages = tableData.filter((item) => !item.imgPath).length;
  const doc = buildDocument(tableData);
  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(OUTPUT_DOCX, buffer);

  console.log(`Jumlah data: ${tableData.length}`);
  console.log(`Gambar tidak ditemukan: ${missingImages}`);
  console.log(`File Word tersimpan: ${OUTPUT_DOCX}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
