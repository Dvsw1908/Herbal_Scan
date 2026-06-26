"""
Evaluasi weight model terlatih pada DATA TEST INDEPENDEN (data/test) untuk
SEMUA RUN (model/Hasil N) — mengikuti logika sel "Evaluasi TEST SET" di main.ipynb.

Beda dua jenis metrik (sama seperti notebook):
  - VALIDASI : metrik dari results_{tag}.json (split val final + final bg saat
               training). Optimistis, dipakai monitoring & pemilihan best epoch.
  - TEST     : metrik pada data/test independen yang TIDAK dipakai saat training
               -> indikator generalisasi sebenarnya. Selisih (Val - Test) besar
               menandakan overfitting.

Struktur yang dibaca:
  model/Hasil N/shufflenet_{tag}.pth     (bobot tiap run)
  results/Hasil N/results_{tag}.json     (metrik validasi + class_names)
Output ditulis ke results/Hasil N/:
  cm_test_{tag}.png, results_test_{tag}.json

Data uji: data/test (seluruhnya NoBG).
  - Ground-truth tiap folder dipetakan ke kelas "... NoBG".
  - Ruang prediksi = SEMUA kelas model; prediksi ke kelas BG dihitung SALAH.
  - Folder Mangga (tak dikenal model) & — utk model 16 kelas — folder Rusak dilewati.

Pemakaian:
  python eval_testset.py                 # default: hanya run "Hasil 4"
  python eval_testset.py "Hasil 1"       # run tertentu saja (boleh beberapa)
  python eval_testset.py all             # semua run di model/
"""
import sys
import statistics
from pathlib import Path

# --- pastikan dependency venv ketemu walau launcher venv tidak ada ----------
try:
    import torch
except ModuleNotFoundError:
    _vp = Path(__file__).resolve().parent.parent / "venv" / "Lib" / "site-packages"
    if _vp.exists():
        sys.path.insert(0, str(_vp))
    import torch

import json
import torch.nn as nn
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from torchvision import transforms, models
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             classification_report, confusion_matrix)

BASE_DIR   = Path(__file__).resolve().parent.parent
DATA_DIR   = BASE_DIR / "data"
TEST_DIR   = DATA_DIR / "test"          # data uji independen (NoBG)
MODEL_DIR  = BASE_DIR / "model"
RESULT_DIR = BASE_DIR / "results"
DEFAULT_RUN = "Hasil 4"                  # run yang dievaluasi bila tanpa argumen
DEVICE  = torch.device("cuda" if torch.cuda.is_available() else "cpu")
IMG_EXT = {".jpg", ".jpeg", ".png"}

transform_test = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5]*3, [0.5]*3),
])

SPECIES_KEYWORDS = [
    (("alpukat",),                          "alpukat"),
    (("belimbing", "blbm", "wuluh", "wlh"), "belimbing wuluh"),
    (("jambu",),                            "jambu biji"),
    (("leci",),                             "leci"),
    (("mangga",),                           "mangga"),     # tak dikenal model -> dilewati
    (("nangka",),                           "nangka"),
    (("salam",),                            "salam"),
    (("sirsak",),                           "sirsak"),
    (("srikaya",),                          "srikaya"),
]


def _species_name(cn: str) -> str:
    return (cn.replace(" Rusak NoBG", "").replace(" Rusak BG", "")
              .replace(" NoBG", "").replace(" BG", "").replace(" Rusak", "").strip())

def _get_group(cn: str) -> str:
    is_rusak, is_nobg = "Rusak" in cn, cn.endswith("NoBG")
    if   not is_rusak and not is_nobg: return "Sehat BG"
    elif not is_rusak and     is_nobg: return "Sehat NoBG"
    elif     is_rusak and not is_nobg: return "Rusak BG"
    else:                              return "Rusak NoBG"

def _species_key(cn: str) -> str:
    return _species_name(cn).replace("Daun", "").strip().lower()

def parse_test_folder(name: str):
    low = name.lower()
    sp  = next((canon for keys, canon in SPECIES_KEYWORDS if any(k in low for k in keys)), None)
    return sp, (("rusak" in low) or ("rsk" in low))


class TestDS(Dataset):
    def __init__(self, samples, tf):
        self.samples, self.tf = samples, tf
    def __len__(self):
        return len(self.samples)
    def __getitem__(self, i):
        path, label = self.samples[i]
        return self.tf(Image.open(path).convert("RGB")), label


def build_test_samples(class_names):
    # Ground-truth dipetakan ke kelas "... NoBG"; ruang prediksi tetap semua kelas.
    nobg_map = {(_species_key(cn), "Rusak" in cn): i
                for i, cn in enumerate(class_names) if cn.endswith("NoBG")}
    samples, mapped, skipped = [], {}, {}
    for folder in sorted(TEST_DIR.iterdir()):
        if not folder.is_dir():
            continue
        sp, rusak = parse_test_folder(folder.name)
        imgs = [p for p in folder.iterdir() if p.suffix.lower() in IMG_EXT]
        key  = (sp, rusak)
        if sp is not None and key in nobg_map:
            samples.extend((str(p), nobg_map[key]) for p in imgs)
            mapped[folder.name] = (class_names[nobg_map[key]], len(imgs))
        else:
            skipped[folder.name] = len(imgs)
    return samples, mapped, skipped


def plot_test_cm(y_true, y_pred, class_names, exp_label, out_path):
    group_of = {cn: _get_group(cn) for cn in class_names}
    present  = sorted({group_of[class_names[t]] for t in set(y_true)})
    n_cols   = min(2, len(present))
    n_rows   = (len(present) + n_cols - 1) // n_cols
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols*9, n_rows*7.5), squeeze=False)
    axes = axes.flatten()
    for ax_idx, group in enumerate(present):
        grp_classes  = [cn for cn in class_names if group_of[cn] == group]
        grp_idx_map  = {class_names.index(cn): i for i, cn in enumerate(grp_classes)}
        species_lbls = [_species_name(cn).replace("Daun", "").strip() for cn in grp_classes]
        n = len(grp_classes)
        mask     = [i for i, t in enumerate(y_true) if t in grp_idx_map]
        sub_true = [grp_idx_map[y_true[i]] for i in mask]
        sub_pred = [grp_idx_map.get(y_pred[i], n) for i in mask]
        has_other = any(p == n for p in sub_pred)
        n_pred    = n + 1 if has_other else n
        col_lbls  = species_lbls + (["[Lain]"] if has_other else [])
        cm  = confusion_matrix(sub_true, sub_pred, labels=list(range(n_pred)))
        acc = sum(t == p for t, p in zip(sub_true, sub_pred)) / len(sub_true) if sub_true else 0
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=col_lbls,
                    yticklabels=species_lbls, ax=axes[ax_idx], annot_kws={"size": 8})
        axes[ax_idx].set_title(f"{group}  |  Acc: {acc:.2%}  (n={len(sub_true)})",
                               fontsize=11, fontweight="bold")
        axes[ax_idx].set_xlabel("Predicted"); axes[ax_idx].set_ylabel("True")
        axes[ax_idx].tick_params(axis="x", rotation=45, labelsize=8)
        axes[ax_idx].tick_params(axis="y", rotation=0,  labelsize=8)
    for j in range(len(present), len(axes)):
        axes[j].set_visible(False)
    fig.suptitle(f"[TEST] Confusion Matrix — {exp_label} ({TEST_DIR.name}, NoBG)", fontsize=13)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def evaluate_model(model_dir: Path, result_dir: Path, run_name: str, exp_tag: str, train_pct):
    res_path = result_dir / f"results_{exp_tag}_{train_pct}.json"
    res = json.loads(res_path.read_text(encoding="utf-8"))
    class_names, exp_label = res["class_names"], res["experiment"]
    num_classes = len(class_names)
    val_acc, val_f1 = res.get("accuracy"), res.get("f1_weighted")   # metrik VALIDASI

    model = models.shufflenet_v2_x1_0(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    model.load_state_dict(torch.load(model_dir / f"shufflenet_{exp_tag}_{train_pct}.pth",
                                     map_location=DEVICE))
    model.to(DEVICE).eval()

    samples, mapped, skipped = build_test_samples(class_names)
    loader = DataLoader(TestDS(samples, transform_test), batch_size=64, shuffle=False, num_workers=0)
    y_true, y_pred = [], []
    with torch.no_grad():
        for x, y in loader:
            _, preds = torch.max(model(x.to(DEVICE)), 1)
            y_true.extend(y.numpy().tolist())
            y_pred.extend(preds.cpu().numpy().tolist())

    # metrik TEST (data/test, independen)
    t_acc  = accuracy_score(y_true, y_pred)
    t_prec = precision_score(y_true, y_pred, average="weighted", zero_division=0)
    t_rec  = recall_score(y_true, y_pred, average="weighted", zero_division=0)
    t_f1   = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    report = classification_report(y_true, y_pred, labels=list(range(num_classes)),
                                   target_names=class_names, output_dict=True, zero_division=0)

    gap = (val_acc - t_acc) if val_acc is not None else None
    print(f"\n{'-'*64}\n[{run_name}] {exp_label} | split {train_pct}:{100-train_pct}")
    print(f"  Test: {len(samples)} gambar dari {TEST_DIR.name} | "
          f"folder dipakai={len(mapped)} dilewati={len(skipped)}")
    if skipped:
        print(f"  Dilewati: {', '.join(sorted(skipped))}")
    print(f"  [VALIDASI] (final+final bg, saat training)   Acc={val_acc}  F1={val_f1}")
    print(f"  [TEST]     ({TEST_DIR.name}, independen)         "
          f"Acc={t_acc:.4f}  Prec={t_prec:.4f}  Rec={t_rec:.4f}  F1={t_f1:.4f}")
    if gap is not None:
        print(f"  Selisih akurasi (Validasi - Test) = {gap:+.4f}   (makin besar = makin overfit)")

    plot_test_cm(y_true, y_pred, class_names, exp_label,
                 result_dir / f"cm_test_{exp_tag}_{train_pct}.png")

    (result_dir / f"results_test_{exp_tag}_{train_pct}.json").write_text(json.dumps({
        "run": run_name, "experiment": exp_label, "tag": exp_tag,
        "split_model": f"{train_pct}:{100-train_pct}",
        "eval_type": "TEST (independen)", "test_dir": str(TEST_DIR),
        "num_classes": num_classes, "n_test_images": len(samples),
        "folders_used": mapped, "folders_skipped": skipped,
        "validation_accuracy": val_acc, "validation_f1_weighted": val_f1,
        "test_accuracy": round(t_acc, 4), "test_precision_weighted": round(t_prec, 4),
        "test_recall_weighted": round(t_rec, 4), "test_f1_weighted": round(t_f1, 4),
        "classification_report": report,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    return {"run": run_name, "model": f"{exp_tag}_{train_pct}",
            "val_acc": val_acc, "val_f1": val_f1, "test_acc": t_acc, "test_f1": t_f1,
            "gap": gap, "n": len(samples)}


def discover_runs(selected):
    runs = [d.name for d in sorted(MODEL_DIR.iterdir())
            if d.is_dir() and (RESULT_DIR / d.name).is_dir()]
    if selected:
        runs = [r for r in runs if r in selected]
    return runs


def run_pairs(model_dir: Path):
    pairs = []
    for w in sorted(model_dir.glob("shufflenet_*.pth")):
        exp_tag, train_pct = w.stem.replace("shufflenet_", "").rsplit("_", 1)
        pairs.append((exp_tag, int(train_pct)))
    return pairs


def main():
    args = sys.argv[1:]
    if not args:
        selected = [DEFAULT_RUN]              # default: hanya Hasil 4
    elif [a.lower() for a in args] == ["all"]:
        selected = None                       # semua run
    else:
        selected = args
    runs = discover_runs(selected)
    if not runs:
        tgt = "semua run" if selected is None else ", ".join(selected)
        print(f"Run tidak ditemukan ({tgt}) di {MODEL_DIR}"); return

    rows = []
    for run_name in runs:
        mdir, rdir = MODEL_DIR / run_name, RESULT_DIR / run_name
        print(f"\n{'='*64}\nRUN: {run_name}\n{'='*64}")
        for exp_tag, train_pct in run_pairs(mdir):
            if not (rdir / f"results_{exp_tag}_{train_pct}.json").exists():
                print(f"  ! lewati {exp_tag}_{train_pct}: results_{exp_tag}_{train_pct}.json tidak ada")
                continue
            rows.append(evaluate_model(mdir, rdir, run_name, exp_tag, train_pct))

    if not rows:
        print("\nTidak ada model yang berhasil dievaluasi."); return

    # ── Tabel rinci VALIDASI vs TEST (semua run x model) ─────────────────────
    print(f"\n\n{'='*78}\nPERBANDINGAN VALIDASI vs TEST (test = data/{TEST_DIR.name}, NoBG)\n{'='*78}")
    print(f"{'Run':<10}{'Model':<11}{'Val_Acc':>9}{'Test_Acc':>10}{'Selisih':>10}"
          f"{'Val_F1':>9}{'Test_F1':>9}{'N':>7}")
    for r in rows:
        va = f"{r['val_acc']:.4f}" if r['val_acc'] is not None else "  -  "
        vf = f"{r['val_f1']:.4f}"  if r['val_f1']  is not None else "  -  "
        gp = f"{r['gap']:+.4f}"    if r['gap']     is not None else "  -  "
        print(f"{r['run']:<10}{r['model']:<11}{va:>9}{r['test_acc']:>10.4f}{gp:>10}"
              f"{vf:>9}{r['test_f1']:>9.4f}{r['n']:>7}")

    # ── Rata-rata antar-run per model (hanya relevan bila >1 run) ────────────
    if len(runs) < 2:
        return
    print(f"\n{'='*78}\nRATA-RATA ANTAR-RUN per model  (mean ± std dari {len(runs)} run)\n{'='*78}")
    print(f"{'Model':<11}{'Test_Acc (mean±std)':>24}{'Test_F1 (mean±std)':>24}{'#run':>7}")
    models_seen = sorted({r["model"] for r in rows})
    for m in models_seen:
        accs = [r["test_acc"] for r in rows if r["model"] == m]
        f1s  = [r["test_f1"]  for r in rows if r["model"] == m]
        a_sd = statistics.stdev(accs) if len(accs) > 1 else 0.0
        f_sd = statistics.stdev(f1s)  if len(f1s)  > 1 else 0.0
        acc_str = f"{statistics.mean(accs):.4f} ± {a_sd:.4f}"
        f1_str  = f"{statistics.mean(f1s):.4f} ± {f_sd:.4f}"
        print(f"{m:<11}{acc_str:>24}{f1_str:>24}{len(accs):>7}")


if __name__ == "__main__":
    main()
