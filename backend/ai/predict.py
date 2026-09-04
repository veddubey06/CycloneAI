import importlib


# Load PyTorch dynamically so environments without the PyTorch type stubs do
# not report a static unresolved-import diagnostic.
torch = importlib.import_module("torch")
from pathlib import Path
from PIL import Image

from ai.model import CycloneCNN


# ==========================================
# CONFIGURATION
# ==========================================

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

print("\n==========================================")
print("       CYCLONEAI AI PREDICTION")
print("==========================================\n")

if not MODEL_PATH.exists():

    print("ERROR: Trained model not found.")
    print("Expected:")
    print(MODEL_PATH)
    raise SystemExit

print("Loading trained model...")

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

print("Trained model loaded successfully.")


# ==========================================
# LOAD IMAGE
# ==========================================

if not IMAGE_PATH.exists():

    print("\nERROR: Satellite image not found.")
    print(IMAGE_PATH)
    raise SystemExit

print("\nLoading satellite image...")

image = Image.open(
    IMAGE_PATH
).convert("L")

image = image.resize(
    (IMAGE_SIZE, IMAGE_SIZE)
)


# ==========================================
# IMAGE → TENSOR
# ==========================================

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


# ==========================================
# PREDICTION
# ==========================================

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

    confidence = probabilities[
        predicted_index
    ].item() * 100


# ==========================================
# DISPLAY RESULTS
# ==========================================

print("\n------------------------------------------")

print(
    f"Predicted Pattern : {predicted_class}"
)

print(
    f"Confidence        : {confidence:.2f}%"
)

print("------------------------------------------")

print("\nClass Scores:")

for name, probability in zip(
    CLASSES,
    probabilities
):

    print(
        f"  {name:<15}: "
        f"{probability.item() * 100:.2f}%"
    )


print("\n==========================================")
print("        PREDICTION COMPLETE")
print("==========================================\n")