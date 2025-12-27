"""
MODEL 3: Color Combination Recommender (Color Harmony System)
===================================================================
Independent ML model for recommending perfect color combinations.

Purpose: Analyze color harmony and recommend matching colors based on color theory.
Technology: Color theory algorithms (HSV color wheel, harmony patterns)
Input: Hex color code(s)
Output: Matching colors with harmony scores

Features:
- Complementary colors (180° opposite on color wheel)
- Analogous colors (±30° adjacent colors)
- Triadic colors (120° equidistant colors)
- Split-complementary colors
- Harmony scoring algorithm (0-1 scale)
- Neutral color detection and bonus scoring

Color Theory Rules Implemented:
1. Complementary: Colors opposite on the wheel (high contrast)
2. Analogous: Colors next to each other (harmonious)
3. Triadic: 3 colors equally spaced (balanced)
4. Neutrals: Always work well with any color

Usage:
    recommender = ColorHarmonyRecommender()
    
    # Get complementary color
    complementary = recommender.get_complementary_color('#FF5733')
    
    # Check harmony between two colors
    score = recommender.calculate_harmony('#FF5733', '#3399FF')
    
    # Get all matching colors
    matches = recommender.get_all_matches('#FF5733')
"""

import colorsys
from typing import List, Tuple, Dict
import numpy as np


class ColorHarmonyRecommender:
    """
    Advanced color harmony recommendation system
    Based on traditional color theory and HSV color space
    """
    
    def __init__(self):
        """Initialize color harmony recommender"""
        print("✅ Color Harmony Recommender initialized (Complementary, Analogous, Triadic)")
    
    # =====================================================================
    # CORE COLOR CONVERSION UTILITIES
    # =====================================================================
    
    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """
        Convert hex color to RGB tuple
        Args:
            hex_color: Hex color code (e.g., '#FF5733')
        Returns:
            (R, G, B) tuple (0-255)
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """
        Convert RGB tuple to hex color
        Args:
            rgb: (R, G, B) tuple (0-255)
        Returns:
            Hex color code
        """
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
    
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
    
    # =====================================================================
    # COLOR HARMONY GENERATION
    # =====================================================================
    
    def get_complementary_color(self, hex_color: str) -> str:
        """
        Get complementary color (opposite on color wheel, 180°)
        
        Complementary colors create high contrast and vibrant looks.
        Perfect for: Bold fashion statements, party outfits
        
        Args:
            hex_color: Base hex color code
        Returns:
            Complementary hex color
        """
        rgb = self.hex_to_rgb(hex_color)
        h, s, v = self.rgb_to_hsv(rgb)
        
        # Rotate hue by 180 degrees
        comp_h = (h + 180) % 360
        
        # Convert back
        comp_rgb = self.hsv_to_rgb((comp_h, s, v))
        return self.rgb_to_hex(comp_rgb)
    
    def get_analogous_colors(self, hex_color: str, angle: float = 30) -> List[str]:
        """
        Get analogous colors (adjacent on color wheel, default ±30°)
        
        Analogous colors are harmonious and pleasing to the eye.
        Perfect for: Date nights, casual wear, cohesive looks
        
        Args:
            hex_color: Base hex color code
            angle: Angle offset in degrees (default: 30)
        Returns:
            List of 2 analogous hex colors
        """
        rgb = self.hex_to_rgb(hex_color)
        h, s, v = self.rgb_to_hsv(rgb)
        
        # ±angle degrees
        analog1_h = (h + angle) % 360
        analog2_h = (h - angle) % 360
        
        analog1_rgb = self.hsv_to_rgb((analog1_h, s, v))
        analog2_rgb = self.hsv_to_rgb((analog2_h, s, v))
        
        return [
            self.rgb_to_hex(analog1_rgb),
            self.rgb_to_hex(analog2_rgb)
        ]
    
    def get_triadic_colors(self, hex_color: str) -> List[str]:
        """
        Get triadic colors (120° apart on color wheel)
        
        Triadic colors create balanced, vibrant combinations.
        Perfect for: Creative outfits, fashion-forward looks
        
        Args:
            hex_color: Base hex color code
        Returns:
            List of 2 triadic hex colors
        """
        rgb = self.hex_to_rgb(hex_color)
        h, s, v = self.rgb_to_hsv(rgb)
        
        # 120° and 240° rotations
        triad1_h = (h + 120) % 360
        triad2_h = (h + 240) % 360
        
        triad1_rgb = self.hsv_to_rgb((triad1_h, s, v))
        triad2_rgb = self.hsv_to_rgb((triad2_h, s, v))
        
        return [
            self.rgb_to_hex(triad1_rgb),
            self.rgb_to_hex(triad2_rgb)
        ]
    
    def get_split_complementary_colors(self, hex_color: str) -> List[str]:
        """
        Get split-complementary colors (complementary ± 30°)
        
        Split-complementary offers contrast with less tension than pure complementary.
        Perfect for: Business casual, sophisticated looks
        
        Args:
            hex_color: Base hex color code
        Returns:
            List of 2 split-complementary hex colors
        """
        rgb = self.hex_to_rgb(hex_color)
        h, s, v = self.rgb_to_hsv(rgb)
        
        # Complementary + offset
        base_comp = (h + 180) % 360
        split1_h = (base_comp + 30) % 360
        split2_h = (base_comp - 30) % 360
        
        split1_rgb = self.hsv_to_rgb((split1_h, s, v))
        split2_rgb = self.hsv_to_rgb((split2_h, s, v))
        
        return [
            self.rgb_to_hex(split1_rgb),
            self.rgb_to_hex(split2_rgb)
        ]
    
    def get_monochromatic_colors(self, hex_color: str) -> List[str]:
        """
        Get monochromatic colors (same hue, different saturation/value)
        
        Monochromatic creates elegant, cohesive looks.
        Perfect for: Formal events, minimalist style
        
        Args:
            hex_color: Base hex color code
        Returns:
            List of 3 monochromatic variations
        """
        rgb = self.hex_to_rgb(hex_color)
        h, s, v = self.rgb_to_hsv(rgb)
        
        # Lighter variation
        lighter_rgb = self.hsv_to_rgb((h, max(s - 30, 10), min(v + 20, 100)))
        
        # Darker variation
        darker_rgb = self.hsv_to_rgb((h, min(s + 20, 100), max(v - 30, 20)))
        
        # Desaturated variation
        neutral_rgb = self.hsv_to_rgb((h, max(s - 50, 5), v))
        
        return [
            self.rgb_to_hex(lighter_rgb),
            self.rgb_to_hex(darker_rgb),
            self.rgb_to_hex(neutral_rgb)
        ]
    
    # =====================================================================
    # COLOR HARMONY SCORING
    # =====================================================================
    
    def calculate_harmony(self, hex_color1: str, hex_color2: str) -> float:
        """
        Calculate color harmony score between two colors (0-1)
        
        Scoring based on color theory principles:
        - Complementary: 0.95 (high contrast, bold)
        - Triadic: 0.90 (balanced, vibrant)
        - Analogous: 0.85 (harmonious, cohesive)
        - Split-complementary: 0.80 (sophisticated)
        - Similar: 0.75 (safe, monochromatic)
        - Moderate: 0.65 (acceptable)
        - Poor: 0.50 (avoid)
        
        Bonus scoring for neutral colors (always work well).
        
        Args:
            hex_color1, hex_color2: Hex color codes
        Returns:
            Harmony score (0-1, higher is better)
        """
        rgb1 = self.hex_to_rgb(hex_color1)
        rgb2 = self.hex_to_rgb(hex_color2)
        
        h1, s1, v1 = self.rgb_to_hsv(rgb1)
        h2, s2, v2 = self.rgb_to_hsv(rgb2)
        
        # Calculate hue difference
        hue_diff = abs(h1 - h2)
        if hue_diff > 180:
            hue_diff = 360 - hue_diff
        
        # Check for color harmony patterns
        score = 0.0
        
        # Complementary (180° ± 20°)
        if 160 <= hue_diff <= 200:
            score = 0.95
        
        # Triadic (120° ± 15° or 240° ± 15°)
        elif 105 <= hue_diff <= 135 or 225 <= hue_diff <= 255:
            score = 0.90
        
        # Analogous (30° ± 15°)
        elif hue_diff <= 45:
            score = 0.85
        
        # Split-complementary (150° ± 20°)
        elif 130 <= hue_diff <= 170:
            score = 0.80
        
        # Similar colors (close hue)
        elif hue_diff <= 60:
            score = 0.75
        
        # Moderate difference
        elif 60 <= hue_diff <= 90:
            score = 0.65
        
        # Poor harmony
        else:
            score = 0.50
        
        # Adjust for saturation and value similarity
        sat_diff = abs(s1 - s2)
        val_diff = abs(v1 - v2)
        
        # Penalize extreme saturation/value differences
        if sat_diff > 50 or val_diff > 50:
            score *= 0.85
        
        # Bonus for neutral colors (works with everything)
        if s1 < 20 or s2 < 20:  # Low saturation = neutral
            score = max(score, 0.80)
        
        return score
    
    def is_neutral_color(self, hex_color: str) -> bool:
        """
        Check if color is neutral (black, white, gray, beige, brown)
        
        Neutral colors are versatile and pair well with any color.
        
        Args:
            hex_color: Hex color code
        Returns:
            True if neutral
        """
        rgb = self.hex_to_rgb(hex_color)
        h, s, v = self.rgb_to_hsv(rgb)
        
        # Low saturation = neutral (gray scale)
        if s < 20:
            return True
        
        # Beige/tan/brown colors (low saturation, warm hue)
        if s < 40 and 20 <= h <= 60:
            return True
        
        return False
    
    def get_color_temperature(self, hex_color: str) -> str:
        """
        Determine if color is warm, cool, or neutral
        
        Useful for matching color temperatures in outfits.
        
        Args:
            hex_color: Hex color code
        Returns:
            'warm', 'cool', or 'neutral'
        """
        rgb = self.hex_to_rgb(hex_color)
        h, s, v = self.rgb_to_hsv(rgb)
        
        # Neutral colors
        if s < 20:
            return 'neutral'
        
        # Warm colors: red, orange, yellow (0-60°, 300-360°)
        if h <= 60 or h >= 300:
            return 'warm'
        
        # Cool colors: green, blue, purple (60-300°)
        else:
            return 'cool'
    
    # =====================================================================
    # COMPREHENSIVE MATCHING
    # =====================================================================
    
    def get_all_matches(self, hex_color: str) -> Dict[str, any]:
        """
        Get all possible color matches with scores
        
        Returns comprehensive color recommendations for outfit matching.
        
        Args:
            hex_color: Base hex color code
        Returns:
            Dictionary with all harmony types and their colors
        """
        return {
            'base_color': hex_color,
            'is_neutral': self.is_neutral_color(hex_color),
            'temperature': self.get_color_temperature(hex_color),
            'complementary': {
                'colors': [self.get_complementary_color(hex_color)],
                'score': 0.95,
                'description': 'Bold contrast, high impact'
            },
            'analogous': {
                'colors': self.get_analogous_colors(hex_color),
                'score': 0.85,
                'description': 'Harmonious, easy on the eyes'
            },
            'triadic': {
                'colors': self.get_triadic_colors(hex_color),
                'score': 0.90,
                'description': 'Balanced, vibrant'
            },
            'split_complementary': {
                'colors': self.get_split_complementary_colors(hex_color),
                'score': 0.80,
                'description': 'Sophisticated contrast'
            },
            'monochromatic': {
                'colors': self.get_monochromatic_colors(hex_color),
                'score': 0.75,
                'description': 'Elegant, cohesive'
            }
        }
    
    def recommend_matching_colors(
        self,
        hex_color: str,
        style: str = 'balanced',
        top_n: int = 5
    ) -> List[Dict[str, any]]:
        """
        Get top N matching colors with explanations
        
        Args:
            hex_color: Base color to match
            style: Matching style preference:
                - 'bold': Complementary colors (high contrast)
                - 'harmonious': Analogous colors (similar hues)
                - 'balanced': Mix of all types
                - 'conservative': Neutral and analogous only
            top_n: Number of recommendations to return
        Returns:
            List of matching colors with scores and descriptions
        """
        matches = []
        
        # Get all possible matches
        all_matches = self.get_all_matches(hex_color)
        
        # Filter based on style preference
        if style == 'bold':
            # Prioritize complementary and triadic
            for color in all_matches['complementary']['colors']:
                matches.append({
                    'color': color,
                    'type': 'complementary',
                    'score': 0.95,
                    'description': 'Bold complementary color'
                })
            for color in all_matches['triadic']['colors']:
                matches.append({
                    'color': color,
                    'type': 'triadic',
                    'score': 0.90,
                    'description': 'Vibrant triadic color'
                })
        
        elif style == 'harmonious':
            # Prioritize analogous and monochromatic
            for color in all_matches['analogous']['colors']:
                matches.append({
                    'color': color,
                    'type': 'analogous',
                    'score': 0.85,
                    'description': 'Harmonious analogous color'
                })
            for color in all_matches['monochromatic']['colors']:
                matches.append({
                    'color': color,
                    'type': 'monochromatic',
                    'score': 0.80,
                    'description': 'Cohesive monochromatic shade'
                })
        
        elif style == 'conservative':
            # Only analogous and neutrals
            for color in all_matches['analogous']['colors']:
                if self.is_neutral_color(color) or all_matches['is_neutral']:
                    matches.append({
                        'color': color,
                        'type': 'analogous',
                        'score': 0.90,
                        'description': 'Safe analogous color'
                    })
        
        else:  # balanced
            # Mix of all types
            for harmony_type in ['complementary', 'analogous', 'triadic', 'split_complementary']:
                harmony_data = all_matches[harmony_type]
                for color in harmony_data['colors']:
                    matches.append({
                        'color': color,
                        'type': harmony_type,
                        'score': harmony_data['score'],
                        'description': harmony_data['description']
                    })
        
        # Sort by score and return top N
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:top_n]


# Global recommender instance
_recommender = None

def get_color_harmony_recommender() -> ColorHarmonyRecommender:
    """Get or create global color harmony recommender instance"""
    global _recommender
    if _recommender is None:
        _recommender = ColorHarmonyRecommender()
    return _recommender
