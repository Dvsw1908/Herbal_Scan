"""
Pipeline Pelatihan Utama ShuffleNetV2 — Klasifikasi Spesies Daun Herbal
- Dataset: data/final (tanpa background, hasil rembg)
- Hanya 8 kelas SPESIES (folder "Rusak" dikecualikan — itu domain Skenario 2)
- Split: 80:20 dan 70:30 (Stratified Shuffle Split)
- Train transform: Resize + RandomRotation + RandomHorizontalFlip + Normalize
- Val transform  : Resize + Normalize (tanpa augmentasi)
- Output: model .pth + plot loss/akurasi PNG + results JSON
"""
import json
import random
import time
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
import torchvision.transforms.functional as TF
from pathlib import Path
from torchvision import datasets, transforms, models
from torch.utils.data import Dataset, DataLoader, Subset
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import classification_report

# ======================
# CONFIG
# ======================
BASE_DIR    = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR.parent / "data" / "final"
MODEL_DIR   = BASE_DIR.parent / "model"
RESULT_DIR  = BASE_DIR.parent / "results"

BATCH_SIZE  = 16
EPOCHS      = 10
LR          = 0.001
SEED        = 42

DEVICE       = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SPLIT_RATIOS = [0.8, 0.7]

MODEL_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)

# ======================
# TRANSFORMS (train vs val dipisah)
# ======================
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


# ======================
# WRAPPER: terapkan transform berbeda ke Subset
# ======================
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


# ======================
# HELPER: filter hanya kelas spesies (buang folder "Rusak")
# ======================
def load_species_only(dataset_path: Path) -> tuple:
    """
    Load ImageFolder tanpa transform, lalu buang kelas yang mengandung 'rusak'.
    Label diremap ke 0..N-1 agar tetap kontinu.
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


# ======================
# LOAD DATASET
# ======================
full_dataset, class_names = load_species_only(DATASET_DIR)
num_classes = len(class_names)
all_labels  = np.array([lbl for _, lbl in full_dataset.samples])

print(f"Dataset  : {DATASET_DIR}")
print(f"Total    : {len(full_dataset)} gambar")
print(f"Kelas    : {num_classes} — {class_names}")
print(f"Device   : {DEVICE}")

# ======================
# LOOP SPLIT EKSPERIMEN
# ======================
for split_ratio in SPLIT_RATIOS:
    test_ratio = round(1.0 - split_ratio, 10)
    train_pct  = round(split_ratio * 100)
    test_pct   = 100 - train_pct
    label_str  = f"{train_pct}:{test_pct}"

    print(f"\n{'='*60}")
    print(f"TRAINING — Split {label_str}")

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

    # ======================
    # MODEL (ShuffleNetV2)
    # ======================
    model = models.shufflenet_v2_x1_0(
        weights=models.ShuffleNet_V2_X1_0_Weights.IMAGENET1K_V1
    )
    for p in model.parameters():
        p.requires_grad = False

    model.fc = nn.Linear(model.fc.in_features, num_classes)
    model.to(DEVICE)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.fc.parameters(), lr=LR)

    # ======================
    # TRAINING
    # ======================
    history: list[dict] = []
    start = time.time()

    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            loss = criterion(model(images), labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        avg_loss = running_loss / len(train_loader)

        model.eval()
        correct, total, val_loss = 0, 0, 0.0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(DEVICE), labels.to(DEVICE)
                outputs = model(images)
                val_loss += criterion(outputs, labels).item()
                _, preds = torch.max(outputs, 1)
                correct += (preds == labels).sum().item()
                total   += labels.size(0)

        val_acc     = correct / total
        avg_val_loss = val_loss / len(val_loader)
        history.append({
            "epoch":      epoch + 1,
            "train_loss": round(avg_loss, 4),
            "val_loss":   round(avg_val_loss, 4),
            "val_acc":    round(val_acc, 4),
        })
        print(f"  Epoch {epoch+1}/{EPOCHS}  train_loss={avg_loss:.4f}  val_loss={avg_val_loss:.4f}  val_acc={val_acc:.4f}")

    elapsed = time.time() - start
    print(f"  Selesai dalam {int(elapsed//60)}m {int(elapsed%60)}s")

    # ======================
    # EVALUASI AKHIR
    # ======================
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

    # ======================
    # PLOT LOSS & AKURASI
    # ======================
    ep          = [h["epoch"]      for h in history]
    train_losses = [h["train_loss"] for h in history]
    val_losses   = [h["val_loss"]   for h in history]
    val_accs     = [h["val_acc"]    for h in history]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    ax1.plot(ep, train_losses, "o-", label="Train Loss")
    ax1.plot(ep, val_losses,   "s-", label="Val Loss")
    ax1.set_title(f"Loss — Split {label_str}")
    ax1.set_xlabel("Epoch"); ax1.set_ylabel("Loss"); ax1.legend(); ax1.grid(True)

    ax2.plot(ep, val_accs, "o-", color="green", label="Val Accuracy")
    ax2.set_title(f"Akurasi Validasi — Split {label_str}")
    ax2.set_xlabel("Epoch"); ax2.set_ylabel("Accuracy"); ax2.set_ylim(0, 1)
    ax2.legend(); ax2.grid(True)

    plt.tight_layout()
    plot_path = RESULT_DIR / f"plot_nobg_{train_pct}.png"
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Plot: {plot_path}")

    # ======================
    # SAVE MODEL & JSON
    # ======================
    model_path = MODEL_DIR / f"shufflenet_nobg_{train_pct}.pth"
    torch.save(model.state_dict(), model_path)
    print(f"  Model: {model_path}")

    json_path = RESULT_DIR / f"results_nobg_{train_pct}.json"
    json_path.write_text(json.dumps({
        "experiment":            "nobg_species",
        "split":                 label_str,
        "dataset":               str(DATASET_DIR),
        "num_classes":           num_classes,
        "class_names":           class_names,
        "epochs":                EPOCHS,
        "training_time_sec":     round(elapsed, 2),
        "final_val_accuracy":    round(val_accs[-1], 4),
        "classification_report": report,
        "training_history":      history,
    }, indent=2, ensure_ascii=False))
    print(f"  JSON: {json_path}")

print("\n\nSEMUA EKSPERIMEN SELESAI")
