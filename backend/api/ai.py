from pathlib import Path

import torch  # type: ignore[reportMissingImports]
from PIL import Image
from fastapi import APIRouter  # type: ignore[reportMissingImports]

from ai.model import CycloneCNN


# ==========================================
# CONFIGURATION
# ==========================================

router = APIRouter(
    prefix="/api/ai",
    tags=["AI"]
)

MODEL_PATH = Path("ai/models/cyclone_cnn.pth")

IMAGE_PATH = Path(
    "data/processed/satellite/"
    "nisarga_20200603_1200/"
    "nisarga_b13_geographic_512.png"
)

CLASSES = [
    "Developing",
    "Curved Band",
    "CDO",
    "Sheared",
    "Eye/Eyewall",
    "Weakening"
]

IMAGE_SIZE = 512

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ==========================================
# LOAD MODEL
# ==========================================

model = None

if MODEL_PATH.exists():

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE,
        weights_only=False
    )

    model = CycloneCNN(
        num_classes=len(CLASSES)
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.to(DEVICE)
    model.eval()


# ==========================================
# STATUS
# ==========================================

@router.get("/status")
def ai_status():

    return {
        "ai": "online" if model else "offline",
        "model": "CycloneCNN",
        "trained_model": MODEL_PATH.exists(),
        "device": str(DEVICE),
        "classes": CLASSES
    }


# ==========================================
# PREDICTION
# ==========================================

@router.get("/predict")
def predict():

    if model is None:

        return {
            "status": "error",
            "message": "Trained model not found."
        }

    if not IMAGE_PATH.exists():

        return {
            "status": "error",
            "message": "Satellite image not found."
        }

    image = Image.open(
        IMAGE_PATH
    ).convert("L")

    image = image.resize(
        (IMAGE_SIZE, IMAGE_SIZE)
    )

    tensor = torch.tensor(
        list(image.getdata()),
        dtype=torch.float32
    )

    tensor = tensor.reshape(
        1,
        IMAGE_SIZE,
        IMAGE_SIZE
    )

    tensor = tensor / 255.0

    tensor = tensor.unsqueeze(0)

    tensor = tensor.to(DEVICE)

    with torch.no_grad():

        output = model(tensor)

        probabilities = torch.softmax(
            output,
            dim=1
        )[0]

        predicted_index = torch.argmax(
            probabilities
        ).item()

    predicted_class = CLASSES[
        predicted_index
    ]

    confidence = (
        probabilities[predicted_index].item()
        * 100
    )

    scores = {}

    for index, name in enumerate(CLASSES):

        scores[name] = round(
            probabilities[index].item() * 100,
            2
        )

    return {
        "status": "success",
        "cyclone": "NISARGA",
        "timestamp": "2020-06-03 12:00:00",
        "satellite": "Himawari-8",
        "band": "B13",
        "predicted_pattern": predicted_class,
        "confidence": round(confidence, 2),
        "class_scores": scores
    }