import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "model" / "shufflenet_nobg_70.pth"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

CLASS_NAMES = [
    "Daun Alpukat",
    "Daun Belimbing Wuluh",
    "Daun Jambu biji",
    "Daun Leci",
    "Daun Mangga",
    "Daun Nangka",
    "Daun Sirsak",
    "Daun Srikaya",
]

_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5] * 3, [0.5] * 3),
])


def _load_model() -> nn.Module:
    net = models.shufflenet_v2_x1_0(weights=None)
    net.fc = nn.Linear(net.fc.in_features, len(CLASS_NAMES))
    state = torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True)
    net.load_state_dict(state)
    net.to(DEVICE)
    net.eval()
    return net


_model = _load_model()


def predict_image(image: Image.Image) -> tuple[str, float]:
    tensor = _transform(image).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        logits = _model(tensor)
        probs = torch.softmax(logits, dim=1)
        conf, idx = torch.max(probs, dim=1)
    return CLASS_NAMES[idx.item()], float(conf.item())
