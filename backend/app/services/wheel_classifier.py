from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms
from torchvision.models import resnet18


# backend/app/services/wheel_classifier.py
CURRENT_FILE = Path(__file__).resolve()

# backend/
BACKEND_DIR = CURRENT_FILE.parents[2]

MODEL_PATH = (
    BACKEND_DIR
    / "ai_models"
    / "weights"
    / "wheel_classifier.pt"
)

CLASS_NAMES = [
    "back_with_screw",
    "back_without_screw",
    "front_with_screw",
    "front_without_screw",
]


class WheelClassifier:
    def __init__(self) -> None:
        self.device = torch.device(
            "cuda:0" if torch.cuda.is_available() else "cpu"
        )

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Wheel model not found: {MODEL_PATH}"
            )

        print(f"Loading wheel classifier from: {MODEL_PATH}")
        print(f"Wheel classifier device: {self.device}")

        self.model = resnet18(weights=None)

        self.model.fc = nn.Linear(
            self.model.fc.in_features,
            len(CLASS_NAMES),
        )

        # Your training code saved only model.state_dict()
        checkpoint = torch.load(
        MODEL_PATH,
        map_location=self.device)

        print("Checkpoint Keys:", checkpoint.keys())

        state_dict = checkpoint["model_state_dict"]

        self.class_names = checkpoint["class_names"]

        self.model.load_state_dict(state_dict)

        self.model.to(self.device)
        self.model.eval()

        # This must match your training preprocessing
        self.transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],),])

    def predict(self, image_path: str | Path) -> dict[str, Any]:
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        image = Image.open(image_path).convert("RGB")

        input_tensor = self.transform(image)
        input_tensor = input_tensor.unsqueeze(0)
        input_tensor = input_tensor.to(self.device)

        with torch.inference_mode():
            output = self.model(input_tensor)

            probabilities = torch.softmax(
                output,
                dim=1,
            )

            confidence_tensor, predicted_tensor = torch.max(
                probabilities,
                dim=1,
            )

        predicted_index = predicted_tensor.item()
        confidence = confidence_tensor.item()

        predicted_class = self.class_names[predicted_index]

        return {
            "class_name": predicted_class,
            "class_index": predicted_index,
            "confidence": round(confidence, 6),
            "confidence_percentage": round(
                confidence * 100,
                2,
            ),
        }


# Load only once when FastAPI starts
wheel_classifier = WheelClassifier()
