"""
Eksperimen Skenario 1: Pelatihan Dengan Background vs Tanpa Background
- Dataset "bg"   : data/final bg  (gambar asli dengan background)
- Dataset "nobg" : data/final     (gambar tanpa background, hasil rembg)
- Hanya 8 kelas SPESIES (folder "Rusak" dikecualikan — itu domain Skenario 2)
- Split: 80:20 dan 70:30 (Stratified Shuffle Split)
- Train transform: Resize + RandomRotation + RandomHorizontalFlip + Normalize
- Val transform  : Resize + Normalize (tanpa augmentasi)
- Output: confusion matrix PNG + plot loss/akurasi PNG + results JSON
"""
import json
import random
import time
import torch
import torch.nn as nn
import numpy as np
import torchvision.transforms.functional as TF
from pathlib import Path
from PIL import Image
from torchvision import datasets, transforms, models
from torch.utils.data import Dataset, DataLoader, Subset
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# =====================
# CONFIG
# =====================
BASE_DIR   = Path(__file__).resolve().parent
DATA_DIR   = BASE_DIR.parent / "data"
MODEL_DIR  = BASE_DIR.parent / "model"
RESULT_DIR = BASE_DIR.parent / "results"

EPOCHS     = 10
BATCH_SIZE = 16
LR         = 0.001
SEED       = 42

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

MODEL_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)

DATASETS = {
    "bg":   DATA_DIR / "final bg",
    "nobg": DATA_DIR / "final",
}

SPLIT_RATIOS = [0.8, 0.7]

# =====================
# TRANSFORMS (train vs val dipisah)
# =====================
transform_train = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.Lambda(lambda img: TF.rotate(img, random.choice([0, 90, 180, 270]))),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize([0.5] * 3, [0.5] * 3),
])

transform_val = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5] * 3, [0.5] * 3),
])


# =====================
# WRAPPER: terapkan transform berbeda ke Subset
# =====================
class TransformWrapper(Dataset):
    """Bungkus Subset dengan transform tertentu (train atau val)."""
    def __init__(self, subset: Subset, transform):
        self.subset    = subset
        self.transform = transform

    def __len__(self) -> int:
        return len(self.subset)

    def __getitem__(self, idx: int):
        img, label = self.subset[idx]   # img: PIL Image (dataset tanpa transform)
        return self.transform(img), label


# =====================
# HELPER: filter hanya kelas spesies (buang folder "Rusak")
# =====================
def load_species_only(dataset_path: Path) -> tuple:
    """
    Load ImageFolder tanpa transform, lalu buang kelas yang mengandung 'rusak'.
    Label diremap ke 0..N-1 agar tetap kontinu.
    Return: (dataset_raw, class_names)
    """
    full = datasets.ImageFolder(str(dataset_path))   # transform=None → kembalikan PIL

    valid_cls_idx = [i for i, name in enumerate(full.classes)
                     if "rusak" not in name.lower()]
    valid_set  = set(valid_cls_idx)
    old_to_new = {old: new for new, old in enumerate(valid_cls_idx)}

    full.samples      = [(p, old_to_new[c]) for p, c in full.samples if c in valid_set]
    full.targets      = [c for _, c in full.samples]
    full.classes      = [full.classes[i] for i in valid_cls_idx]
    full.class_to_idx = {name: i for i, name in enumerate(full.classes)}

    return full, full.classes


# =====================
# LOOP EKSPERIMEN
# =====================
for exp_name, dataset_path in DATASETS.items():
    print("\n" + "=" * 70)
    print(f"EKSPERIMEN : {exp_name.upper()}")
    print(f"Dataset    : {dataset_path}")

    full_dataset, class_names = load_species_only(dataset_path)
    num_classes = len(class_names)
    all_labels  = np.array([lbl for _, lbl in full_dataset.samples])

    print(f"Total data : {len(full_dataset)} | Kelas: {num_classes} (spesies, Rusak dikecualikan)")
    print(f"Kelas      : {class_names}")

    for split_ratio in SPLIT_RATIOS:
        test_ratio = round(1.0 - split_ratio, 10)
        train_pct  = round(split_ratio * 100)
        test_pct   = 100 - train_pct
        label_str  = f"{train_pct}:{test_pct}"
        print(f"\n--- Split {label_str} ---")

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

        print(f"Train: {len(train_idx)} | Val: {len(val_idx)}")

        # =====================
        # MODEL
        # =====================
        model = models.shufflenet_v2_x1_0(
            weights=models.ShuffleNet_V2_X1_0_Weights.IMAGENET1K_V1
        )
        for p in model.parameters():
            p.requires_grad = False

        model.fc = nn.Linear(model.fc.in_features, num_classes)
        model.to(DEVICE)

        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(model.fc.parameters(), lr=LR)

        # =====================
        # TRAINING
        # =====================
        training_history: list[dict] = []
        start = time.time()

        for epoch in range(EPOCHS):
            model.train()
            running_loss = 0.0
            for x, y in train_loader:
                x, y = x.to(DEVICE), y.to(DEVICE)
                optimizer.zero_grad()
                loss = criterion(model(x), y)
                loss.backward()
                optimizer.step()
                running_loss += loss.item()
            avg_loss = running_loss / len(train_loader)

            model.eval()
            correct, total, val_loss = 0, 0, 0.0
            with torch.no_grad():
                for x, y in val_loader:
                    x, y = x.to(DEVICE), y.to(DEVICE)
                    out = model(x)
                    val_loss += criterion(out, y).item()
                    _, preds = torch.max(out, 1)
                    correct += (preds == y).sum().item()
                    total += y.size(0)
            val_acc = correct / total

            training_history.append({
                "epoch":      epoch + 1,
                "train_loss": round(avg_loss, 4),
                "val_loss":   round(val_loss / len(val_loader), 4),
                "val_acc":    round(val_acc, 4),
            })
            print(f"  Epoch {epoch+1}/{EPOCHS}  train_loss={avg_loss:.4f}  val_acc={val_acc:.4f}")

        elapsed = time.time() - start
        print(f"  Selesai dalam {int(elapsed//60)}m {int(elapsed%60)}s")

        # =====================
        # EVALUASI AKHIR
        # =====================
        model.eval()
        y_true, y_pred = [], []
        with torch.no_grad():
            for x, y in val_loader:
                _, preds = torch.max(model(x.to(DEVICE)), 1)
                y_true.extend(y.numpy())
                y_pred.extend(preds.cpu().numpy())

        report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)
        print("\n  Classification Report:")
        print(classification_report(y_true, y_pred, target_names=class_names))

        # =====================
        # PLOT LOSS & AKURASI
        # =====================
        ep = [h["epoch"] for h in training_history]
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        ax1.plot(ep, [h["train_loss"] for h in training_history], "o-", label="Train Loss")
        ax1.plot(ep, [h["val_loss"]   for h in training_history], "s-", label="Val Loss")
        ax1.set_title(f"Loss — {exp_name.upper()} | {label_str}")
        ax1.set_xlabel("Epoch"); ax1.set_ylabel("Loss"); ax1.legend(); ax1.grid(True)

        ax2.plot(ep, [h["val_acc"] for h in training_history], "o-", color="green", label="Val Accuracy")
        ax2.set_title(f"Val Accuracy — {exp_name.upper()} | {label_str}")
        ax2.set_xlabel("Epoch"); ax2.set_ylabel("Accuracy"); ax2.set_ylim(0, 1)
        ax2.legend(); ax2.grid(True)
        plt.tight_layout()
        plt.savefig(RESULT_DIR / f"plot_{exp_name}_{train_pct}.png", dpi=120, bbox_inches="tight")
        plt.close()

        # =====================
        # CONFUSION MATRIX
        # =====================
        cm = confusion_matrix(y_true, y_pred)
        fig_sz = max(8, num_classes)
        plt.figure(figsize=(fig_sz, fig_sz - 1))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                    xticklabels=class_names, yticklabels=class_names)
        plt.title(f"Confusion Matrix — {exp_name.upper()} | {label_str}")
        plt.ylabel("True Label"); plt.xlabel("Predicted Label")
        plt.xticks(rotation=45, ha="right"); plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig(RESULT_DIR / f"cm_{exp_name}_{train_pct}.png", dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  CM: {RESULT_DIR / f'cm_{exp_name}_{train_pct}.png'}")

        # =====================
        # SAVE MODEL & JSON
        # =====================
        torch.save(model.state_dict(), MODEL_DIR / f"shufflenet_{exp_name}_{train_pct}.pth")
        print(f"  Model: {MODEL_DIR / f'shufflenet_{exp_name}_{train_pct}.pth'}")

        results = {
            "experiment":            exp_name,
            "split":                 label_str,
            "dataset":               str(dataset_path),
            "num_classes":           num_classes,
            "class_names":           class_names,
            "epochs":                EPOCHS,
            "training_time_sec":     round(elapsed, 2),
            "final_val_accuracy":    training_history[-1]["val_acc"],
            "classification_report": report,
            "training_history":      training_history,
        }
        json_path = RESULT_DIR / f"results_{exp_name}_{train_pct}.json"
        json_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
        print(f"  JSON: {json_path}")

print("\n\nSEMUA EKSPERIMEN SELESAI")
