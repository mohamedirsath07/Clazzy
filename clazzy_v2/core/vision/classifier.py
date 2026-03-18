"""
Clazzy V2 - Multi-Class Clothing Classifier
Upgraded from binary (top/bottom) to 45+ clothing categories
Uses EfficientNet-B0 with custom classification head
"""

import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ClothingClassifier:
    """
    Multi-class clothing classifier using EfficientNet-B0

    Classifies images into:
    - Clothing type (45+ categories)
    - Style attribute (casual, formal, streetwear, etc.)
    - Pattern (solid, striped, checkered, etc.)
    - Season suitability
    """

    # Primary clothing types (expanded from top/bottom)
    CLOTHING_TYPES = [
        # Tops
        "t-shirt", "shirt", "blouse", "polo", "sweater", "hoodie",
        "tank-top", "crop-top", "cardigan", "turtleneck",
        # Bottoms
        "jeans", "trousers", "shorts", "skirt", "chinos", "joggers",
        "leggings", "cargo-pants", "culottes",
        # Outerwear
        "jacket", "blazer", "coat", "windbreaker", "vest",
        "denim-jacket", "leather-jacket", "parka", "bomber-jacket",
        # Dresses
        "casual-dress", "formal-dress", "maxi-dress", "mini-dress",
        "midi-dress", "sundress", "cocktail-dress",
        # Footwear
        "sneakers", "boots", "loafers", "sandals", "heels",
        "flats", "oxford-shoes", "espadrilles",
        # Accessories
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
        model_path: Optional[str] = None,
        device: Optional[str] = None
    ):
        """
        Initialize the classifier

        Args:
            model_path: Path to trained model weights
            device: Device to run inference on (cuda/cpu/mps)
        """
        self.device = device or self._get_device()
        self.num_types = len(self.CLOTHING_TYPES)
        self.num_styles = len(self.STYLE_LABELS)
        self.num_patterns = len(self.PATTERN_LABELS)
        self.num_seasons = len(self.SEASON_LABELS)

        self.model = self._build_model()
        self.transform = self._build_transform()

        if model_path and Path(model_path).exists():
            self._load_weights(model_path)
        else:
            logger.warning("No model weights loaded - using pretrained backbone only")

        self.model.eval()
        self.model.to(self.device)

    def _get_device(self) -> str:
        """Detect best available device"""
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _build_model(self) -> nn.Module:
        """Build multi-head classification model"""
        # Use EfficientNet-B0 as backbone (7.8M params, fast inference)
        backbone = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)

        # Get feature dimension from backbone
        feature_dim = backbone.classifier[1].in_features

        # Remove original classifier
        backbone.classifier = nn.Identity()

        # Multi-head classifier
        model = MultiHeadClassifier(
            backbone=backbone,
            feature_dim=feature_dim,
            num_types=self.num_types,
            num_styles=self.num_styles,
            num_patterns=self.num_patterns,
            num_seasons=self.num_seasons
        )

        return model

    def _build_transform(self) -> transforms.Compose:
        """Build image transformation pipeline"""
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def _load_weights(self, model_path: str):
        """Load trained model weights"""
        try:
            state_dict = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            logger.info(f"Loaded model weights from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model weights: {e}")
            raise

    def preprocess(self, image: Image.Image) -> torch.Tensor:
        """Preprocess image for inference"""
        if image.mode != "RGB":
            image = image.convert("RGB")
        tensor = self.transform(image)
        return tensor.unsqueeze(0)  # Add batch dimension

    @torch.no_grad()
    def predict(
        self,
        image: Image.Image,
        top_k: int = 3
    ) -> Dict:
        """
        Classify clothing item with multi-label predictions

        Args:
            image: PIL Image of clothing item
            top_k: Number of top predictions to return

        Returns:
            Dictionary with predictions for each attribute
        """
        tensor = self.preprocess(image).to(self.device)

        # Get predictions from all heads
        type_logits, style_logits, pattern_logits, season_logits = self.model(tensor)

        # Process type predictions (multi-class)
        type_probs = torch.softmax(type_logits, dim=1)[0]
        type_top_k = torch.topk(type_probs, min(top_k, len(self.CLOTHING_TYPES)))
        type_predictions = [
            {"label": self.CLOTHING_TYPES[idx], "confidence": prob.item()}
            for idx, prob in zip(type_top_k.indices, type_top_k.values)
        ]

        # Process style predictions (multi-label)
        style_probs = torch.sigmoid(style_logits)[0]
        style_predictions = [
            {"label": label, "confidence": prob.item()}
            for label, prob in zip(self.STYLE_LABELS, style_probs)
            if prob > 0.3  # Threshold for multi-label
        ]

        # Process pattern predictions (multi-class)
        pattern_probs = torch.softmax(pattern_logits, dim=1)[0]
        pattern_idx = torch.argmax(pattern_probs)
        pattern_prediction = {
            "label": self.PATTERN_LABELS[pattern_idx],
            "confidence": pattern_probs[pattern_idx].item()
        }

        # Process season predictions (multi-label)
        season_probs = torch.sigmoid(season_logits)[0]
        season_predictions = [
            {"label": label, "confidence": prob.item()}
            for label, prob in zip(self.SEASON_LABELS, season_probs)
            if prob > 0.3
        ]

        # Determine clothing category
        primary_type = type_predictions[0]["label"]
        category = self._get_category(primary_type)

        return {
            "type": {
                "primary": type_predictions[0],
                "alternatives": type_predictions[1:],
            },
            "category": category,
            "style": sorted(style_predictions, key=lambda x: -x["confidence"]),
            "pattern": pattern_prediction,
            "season": season_predictions,
            "metadata": {
                "model": "efficientnet-b0-multihead",
                "device": str(self.device)
            }
        }

    def _get_category(self, clothing_type: str) -> str:
        """Map clothing type to category"""
        category_map = {
            "top": ["t-shirt", "shirt", "blouse", "polo", "sweater", "hoodie",
                   "tank-top", "crop-top", "cardigan", "turtleneck"],
            "bottom": ["jeans", "trousers", "shorts", "skirt", "chinos", "joggers",
                      "leggings", "cargo-pants", "culottes"],
            "outerwear": ["jacket", "blazer", "coat", "windbreaker", "vest",
                         "denim-jacket", "leather-jacket", "parka", "bomber-jacket"],
            "dress": ["casual-dress", "formal-dress", "maxi-dress", "mini-dress",
                     "midi-dress", "sundress", "cocktail-dress"],
            "footwear": ["sneakers", "boots", "loafers", "sandals", "heels",
                        "flats", "oxford-shoes", "espadrilles"],
            "accessory": ["belt", "watch", "hat", "scarf", "bag", "sunglasses"]
        }

        for category, types in category_map.items():
            if clothing_type in types:
                return category
        return "unknown"

    def batch_predict(
        self,
        images: List[Image.Image],
        batch_size: int = 8
    ) -> List[Dict]:
        """Batch inference for multiple images"""
        results = []

        for i in range(0, len(images), batch_size):
            batch = images[i:i + batch_size]
            tensors = torch.cat([self.preprocess(img) for img in batch])
            tensors = tensors.to(self.device)

            with torch.no_grad():
                outputs = self.model(tensors)

            # Process each image in batch
            for j in range(len(batch)):
                result = self._process_single_output(
                    outputs[0][j], outputs[1][j],
                    outputs[2][j], outputs[3][j]
                )
                results.append(result)

        return results

    def _process_single_output(
        self,
        type_logits: torch.Tensor,
        style_logits: torch.Tensor,
        pattern_logits: torch.Tensor,
        season_logits: torch.Tensor
    ) -> Dict:
        """Process output for a single image"""
        type_probs = torch.softmax(type_logits, dim=0)
        type_idx = torch.argmax(type_probs)

        return {
            "type": {
                "primary": {
                    "label": self.CLOTHING_TYPES[type_idx],
                    "confidence": type_probs[type_idx].item()
                }
            },
            "category": self._get_category(self.CLOTHING_TYPES[type_idx])
        }


class MultiHeadClassifier(nn.Module):
    """
    Multi-head classification network
    Shared backbone with separate heads for each attribute
    """

    def __init__(
        self,
        backbone: nn.Module,
        feature_dim: int,
        num_types: int,
        num_styles: int,
        num_patterns: int,
        num_seasons: int,
        dropout: float = 0.3
    ):
        super().__init__()

        self.backbone = backbone

        # Shared feature transformation
        self.shared_fc = nn.Sequential(
            nn.Linear(feature_dim, 512),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(dropout)
        )

        # Type classification head (multi-class)
        self.type_head = nn.Linear(256, num_types)

        # Style classification head (multi-label)
        self.style_head = nn.Linear(256, num_styles)

        # Pattern classification head (multi-class)
        self.pattern_head = nn.Linear(256, num_patterns)

        # Season classification head (multi-label)
        self.season_head = nn.Linear(256, num_seasons)

    def forward(
        self, x: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass through all heads

        Returns:
            Tuple of (type_logits, style_logits, pattern_logits, season_logits)
        """
        # Extract features
        features = self.backbone(x)
        shared = self.shared_fc(features)

        # Classification heads
        type_out = self.type_head(shared)
        style_out = self.style_head(shared)
        pattern_out = self.pattern_head(shared)
        season_out = self.season_head(shared)

        return type_out, style_out, pattern_out, season_out


# Legacy compatibility wrapper
class LegacyClassifierAdapter:
    """
    Adapter to maintain compatibility with V1 API
    Maps new multi-class predictions to simple top/bottom
    """

    def __init__(self, classifier: ClothingClassifier):
        self.classifier = classifier

    def predict_type(self, image: Image.Image) -> Dict:
        """V1-compatible prediction returning top/bottom"""
        result = self.classifier.predict(image)
        category = result["category"]

        # Map to legacy categories
        if category in ["top", "outerwear"]:
            legacy_type = "top"
        elif category in ["bottom"]:
            legacy_type = "bottom"
        elif category == "dress":
            legacy_type = "dress"
        else:
            legacy_type = result["type"]["primary"]["label"]

        return {
            "type": legacy_type,
            "confidence": result["type"]["primary"]["confidence"],
            "detailed": result
        }
