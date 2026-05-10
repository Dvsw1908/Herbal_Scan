"""
Pipeline Pelatihan ShuffleNetV2 — Klasifikasi Daun Herbal

Eksperimen 1 : Sehat saja  — gabungan BG + NoBG, kelas Rusak dikecualikan
Eksperimen 2 : Semua kelas — gabungan BG + NoBG, termasuk Rusak

Split: 80:20 dan 70:30 (Stratified Shuffle Split)
"""

import json
import random
import time
import torch
import torch.nn as nn
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import torchvision.transforms.functional as TF
from pathlib import Path
from PIL import Image
from torchvision import transforms, models
from torchvision.datasets import ImageFolder
from torch.utils.data import Dataset, DataLoader, Subset
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import (classification_report, confusion_matrix,
                             accuracy_score, precision_score,
                             recall_score, f1_score)

# ======================
# CONFIG
# ======================
BASE_DIR   = Path(__file__).resolve().parent
NOBG_DIR   = BASE_DIR.parent / "data" / "final"
BG_DIR     = BASE_DIR.parent / "data" / "final bg"
MODEL_DIR  = BASE_DIR.parent / "model"
RESULT_DIR = BASE_DIR.parent / "results"

BATCH_SIZE   = 16
EPOCHS       = 10
LR           = 0.001
SEED         = 42
DEVICE       = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SPLIT_RATIOS = [0.8, 0.7]

MODEL_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)

# ======================
# TRANSFORMS
# ======================
transform_train = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.Lambda(lambda img: TF.rotate(img, random.choice([0, 90, 180, 270]))),
    transforms.RandomHorizontalFlip(),
    transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0)),
    transforms.ToTensor(),
    transforms.Normalize([0.5] * 3, [0.5] * 3),
])

transform_val = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5] * 3, [0.5] * 3),
])


# ======================
# COMBINED DATASET (BG + NoBG dengan tag nama kelas)
# ======================
class CombinedTaggedDataset(Dataset):
    """
    Menggabungkan dua direktori dataset (BG dan NoBG).
    Nama kelas di-tag: "Daun X BG" dan "Daun X NoBG".
    Jika include_rusak=False, folder yang mengandung kata 'Rusak' dikecualikan.
    """

    def __init__(self, nobg_root: Path, bg_root: Path, include_rusak: bool = True):
        nobg_base = ImageFolder(str(nobg_root))
        bg_base   = ImageFolder(str(bg_root))

        nobg_tagged = {c: f"{c} NoBG" for c in nobg_base.classes}
        bg_tagged   = {c: f"{c} BG"   for c in bg_base.classes}

        all_class_names: list[str] = []
        for orig, tagged in nobg_tagged.items():
            if include_rusak or "Rusak" not in orig:
                if tagged not in all_class_names:
                    all_class_names.append(tagged)
        for orig, tagged in bg_tagged.items():
            if include_rusak or "Rusak" not in orig:
                if tagged not in all_class_names:
                    all_class_names.append(tagged)

        self.classes      = sorted(all_class_names)
        self.class_to_idx = {c: i for i, c in enumerate(self.classes)}

        self.samples: list[tuple[str, int]] = []
        for img_path, orig_label in nobg_base.samples:
            tagged = nobg_tagged[nobg_base.classes[orig_label]]
            if tagged in self.class_to_idx:
                self.samples.append((img_path, self.class_to_idx[tagged]))
        for img_path, orig_label in bg_base.samples:
            tagged = bg_tagged[bg_base.classes[orig_label]]
            if tagged in self.class_to_idx:
                self.samples.append((img_path, self.class_to_idx[tagged]))

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int):
        img_path, label = self.samples[idx]
        return Image.open(img_path).convert("RGB"), label


class TransformWrapper(Dataset):
    def __init__(self, subset: Subset, transform):
        self.subset    = subset
        self.transform = transform

    def __len__(self) -> int:
        return len(self.subset)

    def __getitem__(self, idx: int):
        img, label = self.subset[idx]
        return self.transform(img), label


# ======================
# HELPERS CONFUSION MATRIX
# ======================
def _species_name(class_name: str) -> str:
    return (class_name
            .replace(" Rusak NoBG", "").replace(" Rusak BG", "")
            .replace(" NoBG", "").replace(" BG", "")
            .replace(" Rusak", "").strip())


def _get_group(class_name: str) -> str:
    is_rusak = "Rusak" in class_name
    is_nobg  = class_name.endswith("NoBG")
    if   not is_rusak and not is_nobg: return "Sehat BG"
    elif not is_rusak and     is_nobg: return "Sehat NoBG"
    elif     is_rusak and not is_nobg: return "Rusak BG"
    else:                              return "Rusak NoBG"



def plot_split_cm(y_true, y_pred, class_names, exp_tag, train_pct, exp_label, label_str):
    """Plot confusion matrix terpisah per grup (Sehat BG / Sehat NoBG / Rusak BG / Rusak NoBG)."""
    group_of   = {cn: _get_group(cn) for cn in class_names}
    groups     = sorted(set(group_of.values()))
    n_groups   = len(groups)
    n_cols_fig = 2
    n_rows_fig = (n_groups + 1) // 2

    fig, axes = plt.subplots(n_rows_fig, n_cols_fig,
                             figsize=(n_cols_fig * 9, n_rows_fig * 7.5))
    axes = axes.flatten()

    for ax_idx, group in enumerate(groups):
        grp_classes  = [cn for cn in class_names if group_of[cn] == group]
        grp_idx_map  = {class_names.index(cn): i for i, cn in enumerate(grp_classes)}
        species_lbls = [_species_name(cn) for cn in grp_classes]
        n            = len(grp_classes)

        mask     = [i for i, t in enumerate(y_true) if t in grp_idx_map]
        sub_true = [grp_idx_map[y_true[i]] for i in mask]
        sub_pred = [grp_idx_map.get(y_pred[i], n) for i in mask]

        has_other = any(p == n for p in sub_pred)
        n_pred    = n + 1 if has_other else n
        col_lbls  = species_lbls + (["[Lainnya]"] if has_other else [])

        cm  = confusion_matrix(sub_true, sub_pred, labels=list(range(n_pred)))
        acc = sum(t == p for t, p in zip(sub_true, sub_pred)) / len(sub_true) if sub_true else 0

        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                    xticklabels=col_lbls, yticklabels=species_lbls,
                    ax=axes[ax_idx], annot_kws={"size": 8})
        axes[ax_idx].set_title(f"{group}  |  Acc: {acc:.2%}", fontsize=11, fontweight="bold")
        axes[ax_idx].set_xlabel("Predicted", fontsize=9)
        axes[ax_idx].set_ylabel("True",      fontsize=9)
        axes[ax_idx].tick_params(axis="x", rotation=45, labelsize=8)
        axes[ax_idx].tick_params(axis="y", rotation=0,  labelsize=8)

    for ax_idx in range(n_groups, len(axes)):
        axes[ax_idx].set_visible(False)

    fig.suptitle(f"Confusion Matrix per Grup — {exp_label}\nSplit {label_str}", fontsize=13)
    plt.tight_layout()
    plt.savefig(RESULT_DIR / f"cm_split_{exp_tag}_{train_pct}.png", dpi=150, bbox_inches="tight")
    plt.close()


# ======================
# FUNGSI TRAINING SATU EKSPERIMEN
# ======================
def run_experiment(exp_tag: str, exp_label: str, include_rusak: bool) -> None:
    print(f"\n{'='*60}")
    print(f"EKSPERIMEN: {exp_label}")

    full_dataset = CombinedTaggedDataset(NOBG_DIR, BG_DIR, include_rusak=include_rusak)
    class_names  = full_dataset.classes
    num_classes  = len(class_names)
    all_labels   = np.array([lbl for _, lbl in full_dataset.samples])

    print(f"  Total  : {len(full_dataset)} gambar")
    print(f"  Kelas  : {num_classes}")
    print(f"  Device : {DEVICE}")

    for split_ratio in SPLIT_RATIOS:
        test_ratio = round(1.0 - split_ratio, 10)
        train_pct  = round(split_ratio * 100)
        test_pct   = 100 - train_pct
        label_str  = f"{train_pct}:{test_pct}"

        print(f"\n  --- Split {label_str} ---")

        splitter = StratifiedShuffleSplit(n_splits=1, test_size=test_ratio, random_state=SEED)
        train_idx, val_idx = next(splitter.split(np.zeros(len(all_labels)), all_labels))

        train_loader = DataLoader(
            TransformWrapper(Subset(full_dataset, train_idx), transform_train),
            batch_size=BATCH_SIZE, shuffle=True, num_workers=0,
        )
        val_loader = DataLoader(
            TransformWrapper(Subset(full_dataset, val_idx), transform_val),
            batch_size=BATCH_SIZE, shuffle=False, num_workers=0,
        )
        print(f"  Train: {len(train_idx)} | Val: {len(val_idx)}")

        # --- MODEL ---
        model = models.shufflenet_v2_x1_0(
            weights=models.ShuffleNet_V2_X1_0_Weights.IMAGENET1K_V1
        )
        for p in model.parameters():
            p.requires_grad = False
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        model.to(DEVICE)

        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(model.fc.parameters(), lr=LR)

        # --- TRAINING ---
        history: list[dict] = []
        start = time.time()

        for epoch in range(EPOCHS):
            model.train()
            running_loss, train_correct, train_total = 0.0, 0, 0
            for images, labels in train_loader:
                images, labels = images.to(DEVICE), labels.to(DEVICE)
                optimizer.zero_grad()
                outputs = model(images)
                loss    = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                running_loss  += loss.item()
                _, preds       = torch.max(outputs, 1)
                train_correct += (preds == labels).sum().item()
                train_total   += labels.size(0)
            avg_loss  = running_loss / len(train_loader)
            train_acc = train_correct / train_total

            model.eval()
            correct, total, val_loss = 0, 0, 0.0
            with torch.no_grad():
                for images, labels in val_loader:
                    images, labels = images.to(DEVICE), labels.to(DEVICE)
                    outputs  = model(images)
                    val_loss += criterion(outputs, labels).item()
                    _, preds  = torch.max(outputs, 1)
                    correct  += (preds == labels).sum().item()
                    total    += labels.size(0)

            val_acc      = correct / total
            avg_val_loss = val_loss / len(val_loader)
            history.append({
                "epoch":      epoch + 1,
                "train_loss": round(avg_loss, 4),
                "train_acc":  round(train_acc, 4),
                "val_loss":   round(avg_val_loss, 4),
                "val_acc":    round(val_acc, 4),
            })
            print(f"    Epoch {epoch+1}/{EPOCHS}  train_loss={avg_loss:.4f}  train_acc={train_acc:.4f}"
                  f"  val_loss={avg_val_loss:.4f}  val_acc={val_acc:.4f}")

        elapsed = time.time() - start
        print(f"  Selesai dalam {int(elapsed//60)}m {int(elapsed%60)}s")

        # --- EVALUASI ---
        model.eval()
        y_true, y_pred = [], []
        with torch.no_grad():
            for images, labels in val_loader:
                _, preds = torch.max(model(images.to(DEVICE)), 1)
                y_true.extend(labels.numpy())
                y_pred.extend(preds.cpu().numpy())

        acc   = accuracy_score(y_true, y_pred)
        prec  = precision_score(y_true, y_pred, average="weighted", zero_division=0)
        rec   = recall_score(y_true, y_pred, average="weighted", zero_division=0)
        f1    = f1_score(y_true, y_pred, average="weighted", zero_division=0)
        report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)

        print(f"\n  {'Metric':<12} {'Score':>8}")
        print(f"  {'-'*22}")
        print(f"  {'Accuracy':<12} {acc:>8.4f}")
        print(f"  {'Precision':<12} {prec:>8.4f}")
        print(f"  {'Recall':<12} {rec:>8.4f}")
        print(f"  {'F1-Score':<12} {f1:>8.4f}")

        # --- PLOT LOSS & AKURASI ---
        ep           = [0] + [h["epoch"]      for h in history]
        train_losses = [history[0]["train_loss"]] + [h["train_loss"] for h in history]
        val_losses   = [history[0]["val_loss"]]   + [h["val_loss"]   for h in history]
        train_accs   = [0] + [h["train_acc"] for h in history]
        val_accs     = [0] + [h["val_acc"]   for h in history]

        best = max(history, key=lambda h: h["val_acc"])

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        ax1.plot(ep, train_losses, "r-o", markersize=4, label="Train Loss")
        ax1.plot(ep, val_losses,   "g--s", markersize=4, label="Val Loss")
        ax1.plot(best["epoch"], best["val_loss"], "bo", markersize=8,
                 label=f"Best Epoch {best['epoch']}")
        ax1.set_title(f"Loss — {exp_label}\nSplit {label_str}")
        ax1.set_xlabel("Epoch"); ax1.set_ylabel("Loss"); ax1.legend(); ax1.grid(True)

        ax2.plot(ep, train_accs, "r-o",  markersize=4, label="Train Accuracy")
        ax2.plot(ep, val_accs,   "g--s", markersize=4, label="Val Accuracy")
        ax2.plot(best["epoch"], best["val_acc"], "bo", markersize=8,
                 label=f"Best Epoch {best['epoch']} ({best['val_acc']:.2%})")
        ax2.set_title(f"Akurasi — {exp_label}\nSplit {label_str}")
        ax2.set_xlabel("Epoch"); ax2.set_ylabel("Accuracy")
        ax2.set_ylim(0, 1.05)
        ax2.legend(); ax2.grid(True)

        plt.tight_layout()
        plot_path = RESULT_DIR / f"plot_{exp_tag}_{train_pct}.png"
        plt.savefig(plot_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  Plot : {plot_path}")

        # --- CONFUSION MATRIX (terpisah per grup) ---
        plot_split_cm(y_true, y_pred, class_names,
                      exp_tag, train_pct, exp_label, label_str)
        print(f"  CM Split: {RESULT_DIR / f'cm_split_{exp_tag}_{train_pct}.png'}")

        # --- SAVE MODEL & JSON ---
        model_path = MODEL_DIR / f"shufflenet_{exp_tag}_{train_pct}.pth"
        torch.save(model.state_dict(), model_path)
        print(f"  Model: {model_path}")

        json_path = RESULT_DIR / f"results_{exp_tag}_{train_pct}.json"
        json_path.write_text(json.dumps({
            "experiment":            exp_label,
            "tag":                   exp_tag,
            "split":                 label_str,
            "dataset_nobg":          str(NOBG_DIR),
            "dataset_bg":            str(BG_DIR),
            "include_rusak":         include_rusak,
            "num_classes":           num_classes,
            "class_names":           class_names,
            "epochs":                EPOCHS,
            "training_time_sec":     round(elapsed, 2),
            "accuracy":              round(acc, 4),
            "precision_weighted":    round(prec, 4),
            "recall_weighted":       round(rec, 4),
            "f1_weighted":           round(f1, 4),
            "best_epoch":            best["epoch"],
            "best_val_accuracy":     best["val_acc"],
            "final_train_accuracy":  history[-1]["train_acc"],
            "final_val_accuracy":    history[-1]["val_acc"],
            "classification_report": report,
            "training_history":      history,
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  JSON : {json_path}")


# ======================
# JALANKAN KEDUA EKSPERIMEN
# ======================
print(f"Device  : {DEVICE}")
print(f"NoBG    : {NOBG_DIR}")
print(f"BG      : {BG_DIR}")

run_experiment(
    exp_tag="exp1",
    exp_label="Eksperimen 1 — Sehat (BG + NoBG)",
    include_rusak=True,
)

run_experiment(
    exp_tag="exp2",
    exp_label="Eksperimen 2 — Semua Kondisi (BG + NoBG + Rusak)",
    include_rusak=True,
)

print("\n\nSEMUA EKSPERIMEN SELESAI")
