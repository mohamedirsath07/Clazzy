"""
Clazzy V2 - Fashion Embedding Generator
Uses CLIP for semantic understanding of clothing items
Enables similarity search and outfit compatibility scoring
"""

import torch
import numpy as np
from PIL import Image
from typing import List, Dict, Optional, Union, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Optional imports with graceful fallback
try:
    from transformers import CLIPProcessor, CLIPModel
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False
    logger.warning("CLIP not available. Install transformers package for embedding support.")


class FashionEmbedder:
    """
    Generate embeddings for clothing items using CLIP

    Features:
    - Image embeddings for visual similarity
    - Text embeddings for style descriptions
    - Combined embeddings for outfit compatibility
    """

    # Fashion-specific text prompts for better embeddings
    STYLE_PROMPTS = {
        "casual": "casual relaxed everyday clothing",
        "formal": "formal elegant professional attire",
        "streetwear": "urban streetwear trendy fashion",
        "minimalist": "minimalist clean simple design",
        "bohemian": "bohemian free-spirited artistic style",
        "preppy": "preppy classic collegiate look",
        "athletic": "athletic sporty activewear",
        "vintage": "vintage retro classic fashion",
        "elegant": "elegant sophisticated refined",
        "edgy": "edgy bold statement fashion"
    }

    def __init__(
        self,
        model_name: str = "openai/clip-vit-base-patch32",
        device: Optional[str] = None
    ):
        """
        Initialize the embedder

        Args:
            model_name: HuggingFace model name for CLIP
            device: Device to run on (cuda/cpu/mps)
        """
        if not CLIP_AVAILABLE:
            raise ImportError(
                "CLIP not available. Install with: pip install transformers"
            )

        self.device = device or self._get_device()
        self.model_name = model_name

        logger.info(f"Loading CLIP model: {model_name}")
        self.model = CLIPModel.from_pretrained(model_name)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()

        # Cache for text embeddings
        self._text_embedding_cache = {}

    def _get_device(self) -> str:
        """Detect best available device"""
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    @torch.no_grad()
    def embed_image(self, image: Image.Image) -> np.ndarray:
        """
        Generate embedding for a single image

        Args:
            image: PIL Image

        Returns:
            Normalized embedding vector (512-dim for base model)
        """
        if image.mode != "RGB":
            image = image.convert("RGB")

        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        outputs = self.model.get_image_features(**inputs)
        embedding = outputs.cpu().numpy()[0]

        # L2 normalize
        embedding = embedding / np.linalg.norm(embedding)
        return embedding

    @torch.no_grad()
    def embed_images(
        self,
        images: List[Image.Image],
        batch_size: int = 8
    ) -> np.ndarray:
        """
        Generate embeddings for multiple images

        Args:
            images: List of PIL Images
            batch_size: Batch size for inference

        Returns:
            Array of normalized embeddings (N x embedding_dim)
        """
        all_embeddings = []

        for i in range(0, len(images), batch_size):
            batch = images[i:i + batch_size]
            batch = [img.convert("RGB") if img.mode != "RGB" else img for img in batch]

            inputs = self.processor(images=batch, return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            outputs = self.model.get_image_features(**inputs)
            embeddings = outputs.cpu().numpy()

            # L2 normalize each embedding
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
            all_embeddings.append(embeddings)

        return np.vstack(all_embeddings)

    @torch.no_grad()
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for text description

        Args:
            text: Text description of clothing/style

        Returns:
            Normalized embedding vector
        """
        # Check cache
        if text in self._text_embedding_cache:
            return self._text_embedding_cache[text]

        inputs = self.processor(text=[text], return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        outputs = self.model.get_text_features(**inputs)
        embedding = outputs.cpu().numpy()[0]

        # L2 normalize
        embedding = embedding / np.linalg.norm(embedding)

        # Cache for reuse
        self._text_embedding_cache[text] = embedding
        return embedding

    def compute_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """Compute cosine similarity between two embeddings"""
        return float(np.dot(embedding1, embedding2))

    def compute_image_text_similarity(
        self,
        image: Image.Image,
        text: str
    ) -> float:
        """
        Compute similarity between image and text description

        Useful for matching clothing to style queries like
        "casual summer outfit" or "formal business attire"
        """
        image_emb = self.embed_image(image)
        text_emb = self.embed_text(text)
        return self.compute_similarity(image_emb, text_emb)

    def get_style_scores(self, image: Image.Image) -> Dict[str, float]:
        """
        Score image against all style categories

        Returns:
            Dict mapping style names to similarity scores
        """
        image_emb = self.embed_image(image)

        scores = {}
        for style, prompt in self.STYLE_PROMPTS.items():
            text_emb = self.embed_text(prompt)
            scores[style] = self.compute_similarity(image_emb, text_emb)

        return scores

    def compute_outfit_compatibility(
        self,
        items: List[Image.Image],
        style_query: Optional[str] = None
    ) -> Dict:
        """
        Compute compatibility score for outfit items

        Uses embedding space to measure how well items go together

        Args:
            items: List of clothing item images
            style_query: Optional style filter (e.g., "casual summer")

        Returns:
            Compatibility metrics
        """
        if len(items) < 2:
            return {"score": 1.0, "reason": "Single item"}

        embeddings = self.embed_images(items)

        # Compute pairwise similarities
        pairwise_scores = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                sim = self.compute_similarity(embeddings[i], embeddings[j])
                pairwise_scores.append(sim)

        avg_compatibility = np.mean(pairwise_scores)
        min_compatibility = np.min(pairwise_scores)

        result = {
            "average_score": float(avg_compatibility),
            "min_score": float(min_compatibility),
            "pairwise_scores": pairwise_scores
        }

        # If style query provided, add style alignment score
        if style_query:
            style_emb = self.embed_text(style_query)
            style_scores = [
                self.compute_similarity(emb, style_emb) for emb in embeddings
            ]
            result["style_alignment"] = float(np.mean(style_scores))
            result["overall_score"] = (avg_compatibility + np.mean(style_scores)) / 2
        else:
            result["overall_score"] = avg_compatibility

        return result

    def find_similar_items(
        self,
        query_image: Image.Image,
        item_embeddings: np.ndarray,
        top_k: int = 5
    ) -> List[Tuple[int, float]]:
        """
        Find most similar items from a collection

        Args:
            query_image: Query clothing item
            item_embeddings: Pre-computed embeddings of items (N x dim)
            top_k: Number of results to return

        Returns:
            List of (index, similarity_score) tuples
        """
        query_emb = self.embed_image(query_image)
        similarities = np.dot(item_embeddings, query_emb)

        top_indices = np.argsort(similarities)[::-1][:top_k]

        return [(int(idx), float(similarities[idx])) for idx in top_indices]


class EmbeddingCache:
    """
    Persistent cache for precomputed embeddings
    Avoids recomputation for wardrobe items
    """

    def __init__(self, cache_path: Optional[str] = None):
        self.cache_path = Path(cache_path) if cache_path else None
        self.embeddings: Dict[str, np.ndarray] = {}

        if self.cache_path and self.cache_path.exists():
            self._load_cache()

    def get(self, item_id: str) -> Optional[np.ndarray]:
        """Get cached embedding by item ID"""
        return self.embeddings.get(item_id)

    def set(self, item_id: str, embedding: np.ndarray):
        """Cache embedding for item"""
        self.embeddings[item_id] = embedding
        if self.cache_path:
            self._save_cache()

    def bulk_get(self, item_ids: List[str]) -> Tuple[Dict[str, np.ndarray], List[str]]:
        """
        Get multiple embeddings, return cached and missing IDs

        Returns:
            Tuple of (cached_embeddings_dict, missing_ids_list)
        """
        cached = {}
        missing = []

        for item_id in item_ids:
            if item_id in self.embeddings:
                cached[item_id] = self.embeddings[item_id]
            else:
                missing.append(item_id)

        return cached, missing

    def _load_cache(self):
        """Load embeddings from disk"""
        try:
            data = np.load(self.cache_path, allow_pickle=True)
            self.embeddings = dict(data.item())
            logger.info(f"Loaded {len(self.embeddings)} cached embeddings")
        except Exception as e:
            logger.warning(f"Failed to load embedding cache: {e}")

    def _save_cache(self):
        """Persist embeddings to disk"""
        try:
            np.save(self.cache_path, self.embeddings)
        except Exception as e:
            logger.warning(f"Failed to save embedding cache: {e}")
