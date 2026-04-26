"""
Eksperimen Skenario 2: Klasifikasi Kondisi Daun (Sehat vs Rusak)
- Binary classification berdasarkan nama folder
- Label "rusak" jika nama folder mengandung kata "rusak" (case-insensitive)
  → "Rusak" (kapital) tetap terdeteksi karena pakai .lower()
- Stratified split 80:20
- Train transform: Resize + RandomRotation + GaussianBlur + Normalize
  → GaussianBlur membantu generalisasi ke daun yang lebih rusak/buram
- Val transform  : Resize + Normalize (tanpa augmentasi)
- Output: confusion matrix PNG + results JSON
"""
import json
import random
import time
import torch
import torch.nn as nn
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import torchvision.transforms.functional as TF
from PIL import Image
from pathlib import Path
from torch.utils.data import Dataset, DataLoader, Subset
from torchvision import transforms, models
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import classification_report, confusion_matrix

# =====================
# CONFIG
# =====================
BASE_DIR    = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR.parent / "data" / "resized"
MODEL_DIR   = BASE_DIR.parent / "model"
RESULT_DIR  = BASE_DIR.parent / "results"

EPOCHS      = 10
BATCH_SIZE  = 16
LR          = 0.001
TRAIN_RATIO = 0.8
SEED        = 42

DEVICE      = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CLASS_NAMES = ["sehat", "rusak"]

MODEL_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)

# =====================
# TRANSFORMS (train vs val dipisah)
# =====================
# GaussianBlur → model lebih robust ke daun yang lebih rusak/buram dari dataset
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
        img, label = self.subset[idx]   # img: PIL Image
        return self.transform(img), label


# =====================
# DATASET CUSTOM
# =====================
class LeafConditionDataset(Dataset):
    VALID_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    def __init__(self, root_dir: Path):
        # Tidak ada transform di sini — diterapkan via TransformWrapper
        self.samples: list[tuple[Path, int]] = []

        for folder in sorted(root_dir.iterdir()):
            if not folder.is_dir():
                continue
            # "Rusak" (kapital) → .lower() → "rusak" → terdeteksi ✓
            label = 1 if "rusak" in folder.name.lower() else 0
            for img_file in folder.iterdir():
                if img_file.suffix.lower() in self.VALID_EXTS:
                    self.samples.append((img_file, label))

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int):
        img_path, label = self.samples[idx]
        return Image.open(img_path).convert("RGB"), label   # kembalikan PIL

    def get_labels(self) -> list[int]:
        return [lbl for _, lbl in self.samples]


# =====================
# LOAD + STRATIFIED SPLIT
# =====================
full_dataset = LeafConditionDataset(DATASET_DIR)
labels       = np.array(full_dataset.get_labels())

train_pct = round(TRAIN_RATIO * 100)
test_pct  = 100 - train_pct

splitter = StratifiedShuffleSplit(
    n_splits=1, test_size=round(1.0 - TRAIN_RATIO, 10), random_state=SEED
)
train_idx, val_idx = next(splitter.split(np.zeros(len(labels)), labels))

train_loader = DataLoader(
    TransformWrapper(Subset(full_dataset, train_idx), transform_train),
    batch_size=BATCH_SIZE, shuffle=True, num_workers=0,
)
val_loader = DataLoader(
    TransformWrapper(Subset(full_dataset, val_idx), transform_val),
    batch_size=BATCH_SIZE, shuffle=False, num_workers=0,
)

print(f"Dataset  : {DATASET_DIR}")
print(f"Total    : {len(full_dataset)} | Train {train_pct}%: {len(train_idx)} | Val {test_pct}%: {len(val_idx)}")
print(f"Label    : sehat={int((labels == 0).sum())}  rusak={int((labels == 1).sum())}")
print(f"Train aug: RandomRotation(15°) + GaussianBlur + HorizontalFlip")

# =====================
# MODEL
# =====================
model = models.shufflenet_v2_x1_0(weights=models.ShuffleNet_V2_X1_0_Weights.IMAGENET1K_V1)
for p in model.parameters():
    p.requires_grad = False

model.fc = nn.Linear(model.fc.in_features, len(CLASS_NAMES))
model.to(DEVICE)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.fc.parameters(), lr=LR)

# =====================
# TRAINING
# =====================
history: list[dict] = []
start = time.time()

print(f"\nTraining | device={DEVICE} | epochs={EPOCHS}")
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
    correct, total = 0, 0
    with torch.no_grad():
        for x, y in val_loader:
            x, y = x.to(DEVICE), y.to(DEVICE)
            _, preds = torch.max(model(x), 1)
            correct += (preds == y).sum().item()
            total += y.size(0)
    val_acc = correct / total

    history.append({"epoch": epoch + 1, "loss": round(avg_loss, 4), "val_acc": round(val_acc, 4)})
    print(f"  Epoch {epoch+1}/{EPOCHS}  loss={avg_loss:.4f}  val_acc={val_acc:.4f}")

elapsed = time.time() - start
print(f"\nSelesai dalam {int(elapsed//60)}m {int(elapsed%60)}s")

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

report = classification_report(y_true, y_pred, target_names=CLASS_NAMES, output_dict=True)
print("\nClassification Report:")
print(classification_report(y_true, y_pred, target_names=CLASS_NAMES))

# =====================
# CONFUSION MATRIX
# =====================
cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES)
plt.title(f"Confusion Matrix — Kondisi Daun ({train_pct}:{test_pct})")
plt.ylabel("True Label")
plt.xlabel("Predicted Label")
plt.tight_layout()
cm_path = RESULT_DIR / "cm_condition.png"
plt.savefig(cm_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"Confusion matrix: {cm_path}")

# =====================
# SAVE MODEL & JSON
# =====================
model_path = MODEL_DIR / "shufflenet_condition.pth"
torch.save(model.state_dict(), model_path)
print(f"Model disimpan  : {model_path}")

results = {
    "experiment":         "kondisi_daun",
    "dataset":            str(DATASET_DIR),
    "split":              f"{train_pct}:{test_pct}",
    "train_augmentation": ["RandomRotation(15)", "GaussianBlur(k=3, sigma=0.1-2.0)", "RandomHorizontalFlip"],
    "epochs":             EPOCHS,
    "training_time_sec":  round(elapsed, 2),
    "final_val_accuracy": history[-1]["val_acc"],
    "classification_report": report,
    "training_history":   history,
}
json_path = RESULT_DIR / "results_condition.json"
json_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
print(f"Hasil JSON      : {json_path}")
