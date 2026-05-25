"""
Export shufflenet_exp2_70.pth ke TorchScript mobile format (.ptl)
Output: herbal_leaf_app/assets/model/shufflenet_exp2.ptl
"""

import torch
import torch.nn as nn
from torchvision import models
from torch.utils.mobile_optimizer import optimize_for_mobile
from pathlib import Path

BASE_DIR   = Path(__file__).resolve().parent.parent
MODEL_IN   = BASE_DIR / "model" / "shufflenet_exp2_80.pth"
MODEL_OUT  = BASE_DIR / "herbal_leaf_app" / "assets" / "model" / "shufflenet_exp2.ptl"

CLASS_NAMES = [
    "Daun Alpukat BG",
    "Daun Alpukat NoBG",
    "Daun Alpukat Rusak BG",
    "Daun Alpukat Rusak NoBG",
    "Daun Belimbing Wuluh BG",
    "Daun Belimbing Wuluh NoBG",
    "Daun Belimbing Wuluh Rusak BG",
    "Daun Belimbing Wuluh Rusak NoBG",
    "Daun Jambu Biji Rusak BG",
    "Daun Jambu Biji Rusak NoBG",
    "Daun Jambu biji BG",
    "Daun Jambu biji NoBG",
    "Daun Leci BG",
    "Daun Leci NoBG",
    "Daun Leci Rusak BG",
    "Daun Leci Rusak NoBG",
    "Daun Nangka BG",
    "Daun Nangka NoBG",
    "Daun Nangka Rusak BG",
    "Daun Nangka Rusak NoBG",
    "Daun Salam BG",
    "Daun Salam NoBG",
    "Daun Salam Rusak BG",
    "Daun Salam Rusak NoBG",
    "Daun Sirsak BG",
    "Daun Sirsak NoBG",
    "Daun Sirsak Rusak BG",
    "Daun Sirsak Rusak NoBG",
    "Daun Srikaya BG",
    "Daun Srikaya NoBG",
    "Daun Srikaya Rusak BG",
    "Daun Srikaya Rusak NoBG",
]

print(f"Loading model from: {MODEL_IN}")
net = models.shufflenet_v2_x1_0(weights=None)
net.fc = nn.Linear(net.fc.in_features, len(CLASS_NAMES))
state = torch.load(MODEL_IN, map_location="cpu", weights_only=True)
net.load_state_dict(state)
net.eval()

print("Tracing model...")
example = torch.rand(1, 3, 224, 224)
traced = torch.jit.trace(net, example)

MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)
traced.save(str(MODEL_OUT))

size_mb = MODEL_OUT.stat().st_size / 1024 / 1024
print(f"Saved: {MODEL_OUT}")
print(f"Size : {size_mb:.1f} MB")
