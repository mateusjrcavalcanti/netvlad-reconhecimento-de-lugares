import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from functools import lru_cache
from PIL import Image

from config import NETVLAD_CHECKPOINT_PATH
from netvlad.NetVLAD import NetVLAD


NETVLAD_SEED = 42


def get_base_cnn_model():
    weights = models.ResNet18_Weights.IMAGENET1K_V1
    model = models.resnet18(weights=weights)
    layers = list(model.children())[:-2]
    model = nn.Sequential(*layers)
    return model


@lru_cache(maxsize=1)
def get_descriptor_models():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    torch.manual_seed(NETVLAD_SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(NETVLAD_SEED)

    base_model = get_base_cnn_model().to(device)
    netvlad = NetVLAD(num_clusters=64, dim=512).to(device)

    if NETVLAD_CHECKPOINT_PATH.exists():
        checkpoint = torch.load(NETVLAD_CHECKPOINT_PATH, map_location=device)
        state_dict = checkpoint.get("state_dict", checkpoint) if isinstance(checkpoint, dict) else checkpoint
        netvlad.load_state_dict(state_dict)

    base_model.eval()
    netvlad.eval()

    return device, base_model, netvlad


def preprocess_image(image_path):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    image = Image.open(image_path).convert('RGB')
    return transform(image).unsqueeze(0)


def extract_netvlad_descriptor(image_path):
    device, base_model, netvlad = get_descriptor_models()
    image_tensor = preprocess_image(image_path).to(device)

    with torch.no_grad():
        features = base_model(image_tensor)
        descriptor = netvlad(features)

    return descriptor.cpu().numpy()
