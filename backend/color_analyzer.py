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
- Extended human-readable color names (60+ fashion colors)

Usage:
    analyzer = ColorAnalyzer()
    colors = analyzer.extract_colors(image_bytes)
    # Returns: [{'hex': '#FF5733', 'rgb': (255,87,51), 'percentage': 45.2, 'name': 'Tomato'}]
"""

import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image
import io
from typing import List, Tuple
import colorsys

# Extended color palette with fashion-friendly names (from export_package)
COLOR_NAMES = {
    # Reds
    "Red": "#FF0000", "Dark Red": "#8B0000", "Crimson": "#DC143C", 
    "Maroon": "#800000", "Indian Red": "#CD5C5C", "Fire Brick": "#B22222",
    
    # Pinks
    "Pink": "#FFC0CB", "Hot Pink": "#FF69B4", "Deep Pink": "#FF1493",
    "Light Pink": "#FFB6C1", "Pale Violet Red": "#DB7093", "Salmon": "#FA8072",
    
    # Oranges
    "Orange": "#FFA500", "Dark Orange": "#FF8C00", "Coral": "#FF7F50",
    "Tomato": "#FF6347", "Orange Red": "#FF4500", "Peach": "#FFDAB9",
    
    # Yellows
    "Yellow": "#FFFF00", "Gold": "#FFD700", "Light Yellow": "#FFFFE0",
    "Khaki": "#F0E68C", "Goldenrod": "#DAA520", "Mustard": "#FFDB58",
    
    # Greens
    "Green": "#008000", "Dark Green": "#006400", "Lime": "#00FF00",
    "Forest Green": "#228B22", "Sea Green": "#2E8B57", "Olive": "#808000",
    "Light Green": "#90EE90", "Teal": "#008080", "Mint": "#98FF98",
    
    # Blues
    "Blue": "#0000FF", "Navy": "#000080", "Dark Blue": "#00008B",
    "Royal Blue": "#4169E1", "Steel Blue": "#4682B4", "Sky Blue": "#87CEEB",
    "Light Blue": "#ADD8E6", "Powder Blue": "#B0E0E6", "Cyan": "#00FFFF",
    "Dodger Blue": "#1E90FF", "Cobalt Blue": "#0047AB", "Denim Blue": "#1560BD",
    
    # Purples
    "Purple": "#800080", "Dark Purple": "#301934", "Violet": "#EE82EE",
    "Indigo": "#4B0082", "Lavender": "#E6E6FA", "Orchid": "#DA70D6",
    "Plum": "#DDA0DD", "Magenta": "#FF00FF", "Mauve": "#E0B0FF",
    
    # Browns
    "Brown": "#A52A2A", "Saddle Brown": "#8B4513", "Chocolate": "#D2691E",
    "Sienna": "#A0522D", "Tan": "#D2B48C", "Beige": "#F5F5DC",
    "Wheat": "#F5DEB3", "Camel": "#C19A6B", "Coffee": "#6F4E37",
    
    # Grays
    "Gray": "#808080", "Dark Gray": "#A9A9A9", "Light Gray": "#D3D3D3",
    "Silver": "#C0C0C0", "Dim Gray": "#696969", "Charcoal": "#36454F",
    "Slate Gray": "#708090",
    
    # Black and White
    "Black": "#000000", "White": "#FFFFFF", "Snow": "#FFFAFA",
    "Ivory": "#FFFFF0", "Off White": "#FAF9F6", "Cream": "#FFFDD0",
}

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
            color_name = self._closest_color_name(color_rgb)
            
            result.append({
                'hex': color_hex,
                'rgb': color_rgb,
                'percentage': float(percentages[idx]),
                'hsv': self.rgb_to_hsv(color_rgb),
                'name': color_name
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
        Get human-readable color name using extended palette
        Args:
            hex_color: Hex color code
        Returns:
            Color name (e.g., "Royal Blue", "Coral", "Navy")
        """
        rgb = self.hex_to_rgb(hex_color)
        return self._closest_color_name(rgb)
    
    def _closest_color_name(self, requested_rgb: Tuple[int, int, int]) -> str:
        """Find the closest color name for given RGB values using extended palette."""
        min_dist = float("inf")
        closest_name = "Unknown"
        
        for name, hex_value in COLOR_NAMES.items():
            r, g, b = self.hex_to_rgb(hex_value)
            dist = (r - requested_rgb[0])**2 + (g - requested_rgb[1])**2 + (b - requested_rgb[2])**2
            if dist < min_dist:
                min_dist = dist
                closest_name = name
        
        return closest_name


# Global analyzer instance
_analyzer = None

def get_color_analyzer() -> ColorAnalyzer:
    """Get or create global color analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = ColorAnalyzer()
    return _analyzer
