"""
Pipeline Pelatihan ShuffleNetV2 — Klasifikasi Daun Herbal

Eksperimen 1 : Sehat saja  — gabungan BG + NoBG, kelas Rusak dikecualikan
Eksperimen 2 : Semua kelas — gabungan BG + NoBG, termasuk Rusak
               (confusion matrix menampilkan label "Rusak BG" / "Rusak NoBG")

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
import torchvision.transforms.functional as TF
from pathlib import Path
from PIL import Image
from torchvision import transforms, models
from torchvision.datasets import ImageFolder
from torch.utils.data import Dataset, DataLoader, Subset
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import classification_report, confusion_matrix

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

        # Kumpulkan semua nama kelas yang akan dipakai
        all_class_names: list[str] = []
        for orig, tagged in nobg_tagged.items():
            if include_rusak or "Rusak" not in orig:
                if tagged not in all_class_names:
                    all_class_names.append(tagged)
        for orig, tagged in bg_tagged.items():
            if include_rusak or "Rusak" not in orig:
                if tagged not in all_class_names:
                    all_class_names.append(tagged)

        self.classes       = sorted(all_class_names)
        self.class_to_idx  = {c: i for i, c in enumerate(self.classes)}

        # Kumpulkan path + label
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
        img = Image.open(img_path).convert("RGB")
        return img, label


class TransformWrapper(Dataset):
    """Bungkus Subset dengan transform tertentu (train atau val)."""

    def __init__(self, subset: Subset, transform):
        self.subset    = subset
        self.transform = transform

    def __len__(self) -> int:
        return len(self.subset)

    def __getitem__(self, idx: int):
        img, label = self.subset[idx]
        return self.transform(img), label


# ======================
# CONFUSION MATRIX PLOT
# ======================
def plot_confusion_matrix(cm: np.ndarray, class_names: list[str],
                          title: str, save_path: Path) -> None:
    n = len(class_names)
    fig_size = max(12, n * 0.55)
    fig, ax = plt.subplots(figsize=(fig_size, fig_size * 0.85))

    im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
    plt.colorbar(im, ax=ax)

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(class_names, rotation=90, fontsize=7)
    ax.set_yticklabels(class_names, fontsize=7)
    ax.set_xlabel("Predicted", fontsize=10)
    ax.set_ylabel("True", fontsize=10)
    ax.set_title(title, fontsize=11)

    thresh = cm.max() / 2.0
    for i in range(n):
        for j in range(n):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                    fontsize=6, color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


# ======================
# FUNGSI TRAINING SATU EKSPERIMEN
# ======================
def run_experiment(
    exp_tag: str,
    exp_label: str,
    include_rusak: bool,
) -> None:
    print(f"\n{'='*60}")
    print(f"EKSPERIMEN: {exp_label}")

    full_dataset = CombinedTaggedDataset(NOBG_DIR, BG_DIR, include_rusak=include_rusak)
    class_names  = full_dataset.classes
    num_classes  = len(class_names)
    all_labels   = np.array([lbl for _, lbl in full_dataset.samples])

    print(f"  Total    : {len(full_dataset)} gambar")
    print(f"  Kelas    : {num_classes} — {class_names}")
    print(f"  Device   : {DEVICE}")

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
            running_loss  = 0.0
            train_correct = 0
            train_total   = 0
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
                    _, preds = torch.max(outputs, 1)
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

        report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)
        print("\n  Classification Report:")
        print(classification_report(y_true, y_pred, target_names=class_names))

        # --- PLOT LOSS & AKURASI ---
        ep           = [0] + [h["epoch"]      for h in history]
        train_losses = [history[0]["train_loss"]] + [h["train_loss"] for h in history]
        val_losses   = [history[0]["val_loss"]]   + [h["val_loss"]   for h in history]
        train_accs   = [0] + [h["train_acc"] for h in history]
        val_accs     = [0] + [h["val_acc"]   for h in history]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        ax1.plot(ep, train_losses, "o-", label="Train Loss")
        ax1.plot(ep, val_losses,   "s-", label="Val Loss")
        ax1.set_title(f"Loss — {exp_label} Split {label_str}")
        ax1.set_xlabel("Epoch"); ax1.set_ylabel("Loss"); ax1.legend(); ax1.grid(True)

        ax2.plot(ep, train_accs, "o-", color="blue",  label="Train Accuracy")
        ax2.plot(ep, val_accs,   "s-", color="green", label="Val Accuracy")
        ax2.set_title(f"Akurasi — {exp_label} Split {label_str}")
        ax2.set_xlabel("Epoch"); ax2.set_ylabel("Accuracy"); ax2.set_ylim(0, 1)
        ax2.legend(); ax2.grid(True)

        plt.tight_layout()
        plot_path = RESULT_DIR / f"plot_{exp_tag}_{train_pct}.png"
        plt.savefig(plot_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  Plot: {plot_path}")

        # --- CONFUSION MATRIX ---
        cm = confusion_matrix(y_true, y_pred)
        cm_path = RESULT_DIR / f"cm_{exp_tag}_{train_pct}.png"
        final_train_acc = history[-1]["train_acc"]
        final_val_acc   = round(val_accs[-1], 4)
        plot_confusion_matrix(
            cm, class_names,
            title=(f"Confusion Matrix — {exp_label} | Split {label_str}\n"
                   f"Train Acc: {final_train_acc:.2%}  |  Val Acc: {final_val_acc:.2%}"),
            save_path=cm_path,
        )
        print(f"  CM  : {cm_path}")

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
            "final_val_accuracy":    round(val_accs[-1], 4),
            "classification_report": report,
            "training_history":      history,
        }, indent=2, ensure_ascii=False))
        print(f"  JSON: {json_path}")


# ======================
# JALANKAN KEDUA EKSPERIMEN
# ======================
print(f"Device  : {DEVICE}")
print(f"NoBG    : {NOBG_DIR}")
print(f"BG      : {BG_DIR}")

run_experiment(
    exp_tag="exp1",
    exp_label="Eksperimen 1 — Sehat (BG + NoBG)",
    include_rusak=False,
)

run_experiment(
    exp_tag="exp2",
    exp_label="Eksperimen 2 — Semua Kondisi (BG + NoBG + Rusak)",
    include_rusak=True,
)

print("\n\nSEMUA EKSPERIMEN SELESAI")
