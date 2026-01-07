"""
Color Extraction Module
Extracts dominant color from clothing images using K-Means clustering.

Usage:
    from color_extraction import extract_dominant_color
    color_name, hex_code = extract_dominant_color("image.jpg")
"""

import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image


# Extended color palette with fashion-friendly names
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


def rgb_to_hex(rgb):
    """Convert RGB values to HEX color code."""
    return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def hex_to_rgb(hex_color):
    """Convert hex to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def closest_color_name(requested_rgb):
    """Find the closest color name for given RGB values."""
    min_dist = float("inf")
    closest_name = "Unknown"
    
    for name, hex_value in COLOR_NAMES.items():
        r, g, b = hex_to_rgb(hex_value)
        dist = (r - requested_rgb[0])**2 + (g - requested_rgb[1])**2 + (b - requested_rgb[2])**2
        if dist < min_dist:
            min_dist = dist
            closest_name = name
    
    return closest_name


def extract_dominant_color(image_path, k=3):
    """
    Extract dominant color from a clothing image.
    
    Args:
        image_path: Path to the image file
        k: Number of clusters for K-Means (2-3 recommended)
    
    Returns:
        color_name: Human-readable color name
        hex_color: HEX color code
    """
    # Load image
    img = Image.open(image_path).convert("RGB")
    img = img.resize((200, 200))
    img_np = np.array(img)

    # Convert RGB to HSV
    hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)

    # Background filtering
    h, s, v = cv2.split(hsv)
    mask = (s > 40) & (v > 40) & ~((s < 30) & (v > 200))
    filtered_pixels = img_np[mask]

    # Fallback if mask removes too many pixels
    if len(filtered_pixels) < 100:
        filtered_pixels = img_np.reshape(-1, 3)

    # K-Means clustering
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(filtered_pixels)

    # Dominant cluster
    counts = np.bincount(kmeans.labels_)
    dominant_rgb = kmeans.cluster_centers_[np.argmax(counts)]

    # Convert to HEX and Name
    hex_color = rgb_to_hex(dominant_rgb)
    color_name = closest_color_name(dominant_rgb)

    return color_name, hex_color


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        color_name, hex_code = extract_dominant_color(image_path)
        print(f"Color: {color_name}")
        print(f"HEX: {hex_code}")
    else:
        print("Usage: python color_extraction.py <image_path>")
