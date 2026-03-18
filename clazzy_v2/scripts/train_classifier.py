"""
Clazzy V2 - Multi-Class Classifier Training Script
Trains the EfficientNet-based clothing classifier
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms, models
from PIL import Image
import os
import json
from pathlib import Path
from typing import Dict, List, Tuple
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import model architecture
import sys
sys.path.append(str(Path(__file__).parent.parent))
from core.vision.classifier import MultiHeadClassifier


class FashionDataset(Dataset):
    """
    Fashion dataset for multi-label classification

    Expected directory structure:
    data/
    ├── train/
    │   ├── images/
    │   │   ├── item_001.jpg
    │   │   └── ...
    │   └── labels.json
    └── val/
        ├── images/
        └── labels.json

    labels.json format:
    {
        "item_001.jpg": {
            "type": "t-shirt",
            "styles": ["casual", "streetwear"],
            "pattern": "solid",
            "seasons": ["summer", "spring"]
        }
    }
    """

    CLOTHING_TYPES = [
        "t-shirt", "shirt", "blouse", "polo", "sweater", "hoodie",
        "tank-top", "crop-top", "cardigan", "turtleneck",
        "jeans", "trousers", "shorts", "skirt", "chinos", "joggers",
        "leggings", "cargo-pants", "culottes",
        "jacket", "blazer", "coat", "windbreaker", "vest",
        "denim-jacket", "leather-jacket", "parka", "bomber-jacket",
        "casual-dress", "formal-dress", "maxi-dress", "mini-dress",
        "midi-dress", "sundress", "cocktail-dress",
        "sneakers", "boots", "loafers", "sandals", "heels",
        "flats", "oxford-shoes", "espadrilles",
        "belt", "watch", "hat", "scarf", "bag", "sunglasses"
    ]

    STYLE_LABELS = [
        "casual", "formal", "streetwear", "minimalist", "bohemian",
        "preppy", "athletic", "vintage", "elegant", "edgy"
    ]

    PATTERN_LABELS = [
        "solid", "striped", "checkered", "floral", "geometric",
        "abstract", "polka-dot", "camouflage", "animal-print"
    ]

    SEASON_LABELS = ["spring", "summer", "fall", "winter", "all-season"]

    def __init__(
        self,
        data_dir: str,
        split: str = "train",
        transform=None
    ):
        self.data_dir = Path(data_dir) / split
        self.images_dir = self.data_dir / "images"
        self.transform = transform or self._default_transform(split == "train")

        # Load labels
        labels_path = self.data_dir / "labels.json"
        if labels_path.exists():
            with open(labels_path) as f:
                self.labels = json.load(f)
        else:
            self.labels = {}

        # Get image list
        self.images = list(self.images_dir.glob("*.jpg")) + \
                      list(self.images_dir.glob("*.png")) + \
                      list(self.images_dir.glob("*.webp"))

        logger.info(f"Loaded {len(self.images)} images for {split}")

    def _default_transform(self, is_train: bool):
        """Default transforms with data augmentation for training"""
        if is_train:
            return transforms.Compose([
                transforms.Resize((256, 256)),
                transforms.RandomCrop(224),
                transforms.RandomHorizontalFlip(),
                transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
        else:
            return transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = self.images[idx]
        image = Image.open(img_path).convert("RGB")

        if self.transform:
            image = self.transform(image)

        # Get labels
        filename = img_path.name
        label_data = self.labels.get(filename, {})

        # Encode labels
        type_label = self._encode_type(label_data.get("type", "t-shirt"))
        style_labels = self._encode_styles(label_data.get("styles", []))
        pattern_label = self._encode_pattern(label_data.get("pattern", "solid"))
        season_labels = self._encode_seasons(label_data.get("seasons", ["all-season"]))

        return {
            "image": image,
            "type": type_label,
            "styles": style_labels,
            "pattern": pattern_label,
            "seasons": season_labels
        }

    def _encode_type(self, type_name: str) -> int:
        """Encode type to class index"""
        try:
            return self.CLOTHING_TYPES.index(type_name)
        except ValueError:
            return 0  # Default

    def _encode_styles(self, styles: List[str]) -> torch.Tensor:
        """Encode styles as multi-hot vector"""
        labels = torch.zeros(len(self.STYLE_LABELS))
        for style in styles:
            try:
                idx = self.STYLE_LABELS.index(style)
                labels[idx] = 1
            except ValueError:
                pass
        return labels

    def _encode_pattern(self, pattern: str) -> int:
        """Encode pattern to class index"""
        try:
            return self.PATTERN_LABELS.index(pattern)
        except ValueError:
            return 0

    def _encode_seasons(self, seasons: List[str]) -> torch.Tensor:
        """Encode seasons as multi-hot vector"""
        labels = torch.zeros(len(self.SEASON_LABELS))
        for season in seasons:
            try:
                idx = self.SEASON_LABELS.index(season)
                labels[idx] = 1
            except ValueError:
                pass
        return labels


def create_model(num_types: int, num_styles: int, num_patterns: int, num_seasons: int):
    """Create multi-head classifier model"""
    backbone = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
    feature_dim = backbone.classifier[1].in_features
    backbone.classifier = nn.Identity()

    model = MultiHeadClassifier(
        backbone=backbone,
        feature_dim=feature_dim,
        num_types=num_types,
        num_styles=num_styles,
        num_patterns=num_patterns,
        num_seasons=num_seasons,
        dropout=0.3
    )

    return model


def train_epoch(model, dataloader, optimizer, device, scaler=None):
    """Train for one epoch"""
    model.train()
    total_loss = 0
    correct_type = 0
    total = 0

    ce_loss = nn.CrossEntropyLoss()
    bce_loss = nn.BCEWithLogitsLoss()

    pbar = tqdm(dataloader, desc="Training")
    for batch in pbar:
        images = batch["image"].to(device)
        type_labels = batch["type"].to(device)
        style_labels = batch["styles"].to(device)
        pattern_labels = batch["pattern"].to(device)
        season_labels = batch["seasons"].to(device)

        optimizer.zero_grad()

        with torch.cuda.amp.autocast(enabled=scaler is not None):
            type_out, style_out, pattern_out, season_out = model(images)

            # Compute losses
            loss_type = ce_loss(type_out, type_labels)
            loss_style = bce_loss(style_out, style_labels)
            loss_pattern = ce_loss(pattern_out, pattern_labels)
            loss_season = bce_loss(season_out, season_labels)

            # Combined loss (weighted)
            loss = loss_type * 2.0 + loss_style + loss_pattern + loss_season

        if scaler:
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            optimizer.step()

        total_loss += loss.item()

        # Accuracy for type classification
        _, predicted = type_out.max(1)
        correct_type += predicted.eq(type_labels).sum().item()
        total += type_labels.size(0)

        pbar.set_postfix({
            "loss": f"{loss.item():.4f}",
            "acc": f"{100 * correct_type / total:.2f}%"
        })

    return total_loss / len(dataloader), correct_type / total


def validate(model, dataloader, device):
    """Validate model"""
    model.eval()
    correct_type = 0
    total = 0

    with torch.no_grad():
        for batch in dataloader:
            images = batch["image"].to(device)
            type_labels = batch["type"].to(device)

            type_out, _, _, _ = model(images)

            _, predicted = type_out.max(1)
            correct_type += predicted.eq(type_labels).sum().item()
            total += type_labels.size(0)

    return correct_type / total


def main():
    """Main training function"""
    # Configuration
    config = {
        "data_dir": "./data/fashion",
        "output_dir": "./models/classifier",
        "batch_size": 32,
        "epochs": 30,
        "learning_rate": 1e-4,
        "weight_decay": 1e-5,
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }

    logger.info(f"Training config: {config}")
    device = torch.device(config["device"])

    # Create datasets
    train_dataset = FashionDataset(config["data_dir"], split="train")
    val_dataset = FashionDataset(config["data_dir"], split="val")

    train_loader = DataLoader(
        train_dataset,
        batch_size=config["batch_size"],
        shuffle=True,
        num_workers=4,
        pin_memory=True
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=config["batch_size"],
        shuffle=False,
        num_workers=4
    )

    # Create model
    model = create_model(
        num_types=len(FashionDataset.CLOTHING_TYPES),
        num_styles=len(FashionDataset.STYLE_LABELS),
        num_patterns=len(FashionDataset.PATTERN_LABELS),
        num_seasons=len(FashionDataset.SEASON_LABELS)
    )
    model = model.to(device)

    # Optimizer and scheduler
    optimizer = optim.AdamW(
        model.parameters(),
        lr=config["learning_rate"],
        weight_decay=config["weight_decay"]
    )
    scheduler = optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=config["epochs"]
    )

    # Mixed precision training
    scaler = torch.cuda.amp.GradScaler() if device.type == "cuda" else None

    # Training loop
    best_acc = 0
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    for epoch in range(config["epochs"]):
        logger.info(f"\nEpoch {epoch + 1}/{config['epochs']}")

        train_loss, train_acc = train_epoch(
            model, train_loader, optimizer, device, scaler
        )
        val_acc = validate(model, val_loader, device)

        scheduler.step()

        logger.info(
            f"Train Loss: {train_loss:.4f}, "
            f"Train Acc: {train_acc * 100:.2f}%, "
            f"Val Acc: {val_acc * 100:.2f}%"
        )

        # Save best model
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), output_dir / "clothing_classifier.pt")
            logger.info(f"Saved best model with acc: {val_acc * 100:.2f}%")

    logger.info(f"\nTraining complete. Best validation accuracy: {best_acc * 100:.2f}%")


if __name__ == "__main__":
    main()
