import csv
from pathlib import Path

import torch  # type: ignore[import-not-found]
import torch.nn as nn  # type: ignore[import-not-found]
from PIL import Image
from torch.utils.data import Dataset, DataLoader  # type: ignore[import-not-found]

from ai.model import CycloneCNN


# ==========================================
# CONFIGURATION
# ==========================================

MANIFEST = Path("data/processed/dataset_manifest.csv")

MODEL_DIR = Path("ai/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "cyclone_cnn.pth"

IMAGE_SIZE = 512
BATCH_SIZE = 2
EPOCHS = 20
LEARNING_RATE = 0.001

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ==========================================
# PATTERN CLASSES
# ==========================================

CLASSES = [
    "Developing",
    "Curved Band",
    "CDO",
    "Sheared",
    "Eye/Eyewall",
    "Weakening"
]


# ==========================================
# DATASET
# ==========================================

class CycloneDataset(Dataset):

    def __init__(self, manifest):

        self.samples = []

        with open(manifest, "r", encoding="utf-8") as file:

            reader = csv.DictReader(file)

            for row in reader:

                image_path = Path(row["image_path"])

                if not image_path.exists():
                    continue

                # Prototype label:
                # Current NISARGA samples are early/developing
                label = "Developing"

                self.samples.append(
                    (
                        image_path,
                        CLASSES.index(label)
                    )
                )

        print(f"Usable training samples: {len(self.samples)}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):

        image_path, label = self.samples[index]

        image = Image.open(image_path).convert("L")

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

        return tensor, label


# ==========================================
# TRAINING
# ==========================================

def main():

    print("\n==========================================")
    print("        CYCLONEAI CNN TRAINING")
    print("==========================================\n")

    print("Device:", DEVICE)

    dataset = CycloneDataset(MANIFEST)

    if len(dataset) == 0:

        print("\nERROR: No usable training images found.")
        return

    loader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True
    )

    model = CycloneCNN(
        num_classes=len(CLASSES)
    ).to(DEVICE)

    criterion = nn.CrossEntropyLoss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE
    )

    print("\nStarting training...\n")

    model.train()

    for epoch in range(EPOCHS):

        total_loss = 0
        correct = 0
        total = 0

        for images, labels in loader:

            images = images.to(DEVICE)
            labels = labels.to(DEVICE)

            optimizer.zero_grad()

            outputs = model(images)

            loss = criterion(
                outputs,
                labels
            )

            loss.backward()

            optimizer.step()

            total_loss += loss.item()

            predictions = outputs.argmax(
                dim=1
            )

            correct += (
                predictions == labels
            ).sum().item()

            total += labels.size(0)

        accuracy = (
            100 * correct / total
        )

        average_loss = (
            total_loss / len(loader)
        )

        print(
            f"Epoch {epoch + 1:02d}/{EPOCHS} | "
            f"Loss: {average_loss:.4f} | "
            f"Accuracy: {accuracy:.2f}%"
        )

    # ======================================
    # SAVE MODEL
    # ======================================

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "classes": CLASSES,
            "image_size": IMAGE_SIZE
        },
        MODEL_PATH
    )

    print("\n==========================================")
    print("        TRAINING COMPLETED")
    print("==========================================")

    print("\nModel saved:")
    print(MODEL_PATH)

    print("\nClasses:")

    for index, name in enumerate(CLASSES):
        print(f"{index}: {name}")

    print("\n==========================================\n")


if __name__ == "__main__":
    main()