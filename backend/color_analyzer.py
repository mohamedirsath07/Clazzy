"""
MODEL 2: Color Extraction Model
===================================================================
Independent ML model for extracting and analyzing colors from clothing images.

Purpose: Extract dominant colors from images using K-means clustering algorithm.
Technology: K-means clustering with sklearn, OpenCV for image processing
Input: Image bytes
Output: List of dominant colors with RGB, HEX, HSV values and percentages

Features:
- K-means clustering for multi-color extraction (top 5 colors)
- Color space conversions (RGB ↔ HSV ↔ HEX)
- Percentage calculation for each color
- Smart filtering (removes shadows and overexposure)
- Human-readable color names

Usage:
    analyzer = ColorAnalyzer()
    colors = analyzer.extract_colors(image_bytes)
    # Returns: [{'hex': '#FF5733', 'rgb': (255,87,51), 'percentage': 45.2, 'hsv': ...}]
"""

import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image
import io
from typing import List, Tuple
import colorsys

class ColorAnalyzer:
    """
    Advanced color extraction and harmony analysis
    """
    
    def __init__(self):
        """Initialize color analyzer"""
        self.n_colors = 5  # Extract top 5 colors
        print("✅ Color Analyzer initialized with K-means clustering")
    
    def extract_colors(self, img_bytes: bytes) -> List[dict]:
        """
        Extract dominant colors using K-means clustering
        Args:
            img_bytes: Raw image bytes
        Returns:
            List of colors with hex codes and percentages
            [
                {'hex': '#FF5733', 'rgb': (255, 87, 51), 'percentage': 45.2},
                ...
            ]
        """
        # Load image
        img = Image.open(io.BytesIO(img_bytes))
        
        # Convert to RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize for performance (max 300px)
        max_size = 300
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Reshape to 2D array of pixels (N, 3)
        pixels = img_array.reshape(-1, 3)
        
        # Remove very dark pixels (likely shadows/background)
        # Remove very light pixels (likely overexposed/background)
        brightness = np.mean(pixels, axis=1)
        mask = (brightness > 20) & (brightness < 235)
        filtered_pixels = pixels[mask]
        
        if len(filtered_pixels) < 100:
            # If too few pixels, use all
            filtered_pixels = pixels
        
        # Apply K-means clustering
        n_clusters = min(self.n_colors, len(filtered_pixels))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        kmeans.fit(filtered_pixels)
        
        # Get cluster centers (dominant colors)
        colors = kmeans.cluster_centers_.astype(int)
        
        # Get cluster labels
        labels = kmeans.labels_
        
        # Calculate color percentages
        label_counts = np.bincount(labels)
        percentages = (label_counts / len(labels)) * 100
        
        # Sort by percentage (descending)
        sorted_indices = np.argsort(percentages)[::-1]
        
        # Build result
        result = []
        for idx in sorted_indices:
            color_rgb = tuple(colors[idx])
            color_hex = '#{:02x}{:02x}{:02x}'.format(*color_rgb)
            
            result.append({
                'hex': color_hex,
                'rgb': color_rgb,
                'percentage': float(percentages[idx]),
                'hsv': self.rgb_to_hsv(color_rgb)
            })
        
        return result
    
    def get_dominant_color(self, img_bytes: bytes) -> str:
        """
        Get single most dominant color
        Args:
            img_bytes: Raw image bytes
        Returns:
            Hex color code
        """
        colors = self.extract_colors(img_bytes)
        if colors:
            return colors[0]['hex']
        return '#808080'  # Gray fallback
    
    def rgb_to_hsv(self, rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """
        Convert RGB to HSV color space
        Args:
            rgb: (R, G, B) tuple (0-255)
        Returns:
            (H, S, V) tuple (H: 0-360, S: 0-100, V: 0-100)
        """
        r, g, b = [x / 255.0 for x in rgb]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return (h * 360, s * 100, v * 100)
    
    def hsv_to_rgb(self, hsv: Tuple[float, float, float]) -> Tuple[int, int, int]:
        """
        Convert HSV to RGB color space
        Args:
            hsv: (H, S, V) tuple (H: 0-360, S: 0-100, V: 0-100)
        Returns:
            (R, G, B) tuple (0-255)
        """
        h, s, v = hsv
        r, g, b = colorsys.hsv_to_rgb(h / 360, s / 100, v / 100)
        return (int(r * 255), int(g * 255), int(b * 255))
    
    def rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex color"""
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
    
    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def get_color_name(self, hex_color: str) -> str:
        """
        Get human-readable color name
        Args:
            hex_color: Hex color code
        Returns:
            Color name (e.g., "Red", "Blue", "Neutral")
        """
        rgb = self.hex_to_rgb(hex_color)
        h, s, v = self.rgb_to_hsv(rgb)
        
        # Check for neutral colors
        if s < 20:
            if v > 80:
                return "White"
            elif v < 20:
                return "Black"
            else:
                return "Gray"
        
        # Determine hue-based color name
        if h < 15 or h >= 345:
            return "Red"
        elif h < 45:
            return "Orange"
        elif h < 75:
            return "Yellow"
        elif h < 165:
            return "Green"
        elif h < 255:
            return "Blue"
        elif h < 285:
            return "Purple"
        elif h < 345:
            return "Pink"
        else:
            return "Red"


# Global analyzer instance
_analyzer = None

def get_color_analyzer() -> ColorAnalyzer:
    """Get or create global color analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = ColorAnalyzer()
    return _analyzer
