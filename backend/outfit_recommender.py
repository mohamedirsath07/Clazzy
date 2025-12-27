"""
Intelligent Outfit Recommendation Engine
Integrates all 3 independent ML models to create complete outfit recommendations.

Dependencies:
- MODEL 1: Clothing Classifier (ml_classifier.py) - for style similarity
- MODEL 2: Color Extractor (color_analyzer.py) - not directly used here
- MODEL 3: Color Harmony Recommender (color_harmony.py) - for color matching

Combines:
- Deep learning embeddings for style similarity
- Color theory for harmony matching
- Rule-based systems for occasion appropriateness
"""

import numpy as np
from typing import List, Dict, Tuple
from color_harmony import get_color_harmony_recommender
from ml_classifier import get_classifier

class OutfitRecommender:
    """
    Advanced outfit recommendation using:
    - Deep learning embeddings for style similarity
    - Color theory for harmony matching
    - Rule-based systems for occasion appropriateness
    """
    
    def __init__(self):
        """Initialize recommender with ML models"""
        self.color_harmony = get_color_harmony_recommender()  # MODEL 3
        self.classifier = get_classifier()  # MODEL 1
        
        # Occasion-based rules
        self.occasion_rules = {
            'casual': {
                'preferred_combinations': [
                    ('top', 'bottom'),
                    ('dress',),
                ],
                'color_style': 'relaxed',  # Allow more variety
                'formality': 0.3
            },
            'formal': {
                'preferred_combinations': [
                    ('blazer', 'top', 'bottom'),
                    ('dress',),
                    ('top', 'bottom')
                ],
                'color_style': 'conservative',  # Complementary or analogous
                'formality': 0.9
            },
            'business': {
                'preferred_combinations': [
                    ('blazer', 'top', 'bottom'),
                    ('blazer', 'dress'),
                    ('top', 'bottom')
                ],
                'color_style': 'professional',  # Neutral + accent
                'formality': 0.8
            },
            'party': {
                'preferred_combinations': [
                    ('dress',),
                    ('top', 'bottom'),
                    ('blazer', 'top', 'bottom')
                ],
                'color_style': 'bold',  # Complementary, triadic
                'formality': 0.5
            },
            'date': {
                'preferred_combinations': [
                    ('dress',),
                    ('top', 'bottom'),
                ],
                'color_style': 'harmonious',  # Analogous colors
                'formality': 0.6
            },
            'sports': {
                'preferred_combinations': [
                    ('top', 'bottom'),
                ],
                'color_style': 'vibrant',  # Any colors OK
                'formality': 0.2
            }
        }
        
        print("✅ Outfit Recommender initialized (integrates all 3 ML models)")
    
    def recommend_outfits(
        self,
        clothing_items: List[Dict],
        occasion: str,
        max_outfits: int = 5,
        items_per_outfit: int = 2
    ) -> List[Dict]:
        """
        Generate intelligent outfit recommendations
        
        Args:
            clothing_items: List of items with:
                {
                    'id': str,
                    'type': str,
                    'colors': List[dict],
                    'dominant_color': str,
                    'features': np.ndarray,
                    'url': str
                }
            occasion: Occasion type
            max_outfits: Maximum number of outfits to generate
            items_per_outfit: Target items per outfit
        
        Returns:
            List of outfit recommendations with scores
        """
        if not clothing_items:
            return []
        
        # Get occasion rules
        rules = self.occasion_rules.get(occasion, self.occasion_rules['casual'])
        
        # Group items by type
        items_by_type = {}
        for item in clothing_items:
            item_type = item.get('type', 'other')
            if item_type not in items_by_type:
                items_by_type[item_type] = []
            items_by_type[item_type].append(item)
        
        # Generate outfit combinations
        outfits = []
        
        # Try each preferred combination pattern
        for combination in rules['preferred_combinations']:
            generated = self._generate_combinations(
                items_by_type,
                combination,
                occasion,
                rules,
                max_outfits - len(outfits)
            )
            outfits.extend(generated)
            
            if len(outfits) >= max_outfits:
                break
        
        # Sort by score (descending)
        outfits.sort(key=lambda x: x['score'], reverse=True)
        
        return outfits[:max_outfits]
    
    def _generate_combinations(
        self,
        items_by_type: Dict[str, List[Dict]],
        combination_pattern: Tuple[str, ...],
        occasion: str,
        rules: Dict,
        max_combinations: int
    ) -> List[Dict]:
        """
        Generate outfit combinations for a specific pattern
        
        Args:
            items_by_type: Items grouped by type
            combination_pattern: Tuple of types (e.g., ('top', 'bottom'))
            occasion: Occasion type
            rules: Occasion-specific rules
            max_combinations: Maximum combinations to generate
        
        Returns:
            List of outfit dictionaries
        """
        outfits = []
        
        # Check if we have all required types
        available_types = set(items_by_type.keys())
        required_types = set(combination_pattern)
        
        if not required_types.issubset(available_types):
            return outfits
        
        # Generate combinations recursively
        def generate_recursive(pattern_index: int, current_outfit: List[Dict], used_items: set):
            if pattern_index >= len(combination_pattern):
                # Complete outfit - validate no duplicate types
                outfit_types = [item.get('type') for item in current_outfit]
                
                # CRITICAL FIX: Reject outfits with duplicate types (e.g., top + top)
                if len(outfit_types) != len(set(outfit_types)):
                    return  # Skip this invalid combination
                
                # Calculate score
                score = self._calculate_outfit_score(current_outfit, occasion, rules)
                
                outfits.append({
                    'items': current_outfit.copy(),
                    'score': score,
                    'total_items': len(current_outfit),
                    'occasion': occasion
                })
                return
            
            if len(outfits) >= max_combinations:
                return
            
            # Get items for current type
            current_type = combination_pattern[pattern_index]
            available_items = items_by_type.get(current_type, [])
            
            # Try each item of this type (ONLY items not already used)
            for item in available_items[:10]:  # Limit to top 10 per type
                if len(outfits) >= max_combinations:
                    break
                
                # Get unique identifier for this item
                item_id = item.get('id') or item.get('filename') or str(item)
                
                # Skip if this exact item is already in the outfit
                if item_id in used_items:
                    continue
                
                # NOTE: Removed duplicate type check because ML classification is unreliable
                # Color harmony and visual similarity will ensure good outfit combinations
                
                # Add item to outfit
                current_outfit.append(item)
                used_items.add(item_id)
                
                # Continue with next type
                generate_recursive(pattern_index + 1, current_outfit, used_items)
                
                # Backtrack
                current_outfit.pop()
                used_items.remove(item_id)
        
        # Start generation
        generate_recursive(0, [], set())
        
        return outfits
    
    def _calculate_outfit_score(
        self,
        outfit_items: List[Dict],
        occasion: str,
        rules: Dict
    ) -> float:
        """
        Calculate comprehensive outfit score (0-1)
        
        Scoring factors:
        1. Color harmony (40%)
        2. Style similarity (30%)
        3. Occasion appropriateness (20%)
        4. Item variety (10%)
        
        Args:
            outfit_items: List of items in outfit
            occasion: Occasion type
            rules: Occasion rules
        
        Returns:
            Score (0-1)
        """
        if not outfit_items:
            return 0.0
        
        # 1. Color Harmony Score (40%)
        color_score = self._calculate_color_harmony(outfit_items, rules['color_style'])
        
        # 2. Style Similarity Score (30%)
        style_score = self._calculate_style_similarity(outfit_items)
        
        # 3. Occasion Appropriateness (20%)
        occasion_score = self._calculate_occasion_fit(outfit_items, rules)
        
        # 4. Item Variety Score (10%)
        variety_score = len(outfit_items) / 3.0  # 3 items = perfect variety
        variety_score = min(variety_score, 1.0)
        
        # Weighted average
        total_score = (
            color_score * 0.40 +
            style_score * 0.30 +
            occasion_score * 0.20 +
            variety_score * 0.10
        )
        
        return total_score
    
    def _calculate_color_harmony(
        self,
        outfit_items: List[Dict],
        color_style: str
    ) -> float:
        """
        Calculate color harmony score for outfit using MODEL 3
        
        Args:
            outfit_items: List of items
            color_style: Style preference from occasion rules
        
        Returns:
            Harmony score (0-1)
        """
        if len(outfit_items) < 2:
            return 0.85  # Single item - neutral score
        
        # Get dominant colors
        colors = [item.get('dominant_color', '#808080') for item in outfit_items]
        
        # Calculate pairwise harmony scores using MODEL 3
        harmony_scores = []
        
        for i in range(len(colors)):
            for j in range(i + 1, len(colors)):
                # Use Color Harmony Recommender (MODEL 3)
                score = self.color_harmony.calculate_harmony(colors[i], colors[j])
                harmony_scores.append(score)
        
        if not harmony_scores:
            return 0.85
        
        # Average harmony
        avg_harmony = np.mean(harmony_scores)
        
        # Adjust based on color style preference
        if color_style == 'conservative':
            # Penalize bold color combinations
            if avg_harmony > 0.90:
                avg_harmony *= 0.95
        elif color_style == 'bold':
            # Reward complementary colors
            if 0.90 <= avg_harmony <= 0.95:
                avg_harmony = min(avg_harmony * 1.05, 1.0)
        elif color_style == 'professional':
            # Prefer neutral + accent combinations
            neutral_count = sum(1 for item in outfit_items 
                              if self.color_harmony.is_neutral_color(item.get('dominant_color', '#808080')))
            if neutral_count >= 1:
                avg_harmony = min(avg_harmony * 1.10, 1.0)
        
        return float(avg_harmony)
    
    def _calculate_style_similarity(self, outfit_items: List[Dict]) -> float:
        """
        Calculate style similarity using deep learning embeddings
        
        Args:
            outfit_items: List of items with 'features' field
        
        Returns:
            Similarity score (0-1)
        """
        if len(outfit_items) < 2:
            return 0.80
        
        # Get feature vectors
        features_list = []
        for item in outfit_items:
            if 'features' in item and item['features'] is not None:
                features_list.append(item['features'])
        
        if len(features_list) < 2:
            return 0.75  # No features available
        
        # Calculate pairwise cosine similarities
        similarities = []
        
        for i in range(len(features_list)):
            for j in range(i + 1, len(features_list)):
                sim = self.classifier.compute_similarity(
                    features_list[i],
                    features_list[j]
                )
                similarities.append(sim)
        
        if not similarities:
            return 0.75
        
        # Average similarity
        # Higher similarity = more cohesive style
        avg_similarity = np.mean(similarities)
        
        # Normalize to 0.6-1.0 range (avoid too low scores)
        normalized = 0.6 + (avg_similarity * 0.4)
        
        return float(normalized)
    
    def _calculate_occasion_fit(self, outfit_items: List[Dict], rules: Dict) -> float:
        """
        Calculate how well outfit fits the occasion
        
        Args:
            outfit_items: List of items
            rules: Occasion rules
        
        Returns:
            Fit score (0-1)
        """
        formality_required = rules.get('formality', 0.5)
        
        # Calculate outfit formality
        formality_scores = {
            'dress': 0.7,
            'blazer': 0.9,
            'top': 0.5,
            'bottom': 0.5,
            'shoes': 0.6,
            'other': 0.4
        }
        
        outfit_formality = np.mean([
            formality_scores.get(item.get('type', 'other'), 0.5)
            for item in outfit_items
        ])
        
        # Calculate difference from required formality
        formality_diff = abs(outfit_formality - formality_required)
        
        # Convert to score (smaller difference = higher score)
        fit_score = 1.0 - (formality_diff * 0.8)
        fit_score = max(fit_score, 0.5)  # Minimum 0.5
        
        return float(fit_score)
    
    def _is_neutral_color(self, hex_color: str) -> bool:
        """
        Check if color is neutral using MODEL 3
        
        Args:
            hex_color: Hex color code
        
        Returns:
            True if neutral
        """
        # Use Color Harmony Recommender (MODEL 3)
        return self.color_harmony.is_neutral_color(hex_color)


# Global recommender instance
_recommender = None

def get_outfit_recommender() -> OutfitRecommender:
    """Get or create global outfit recommender instance"""
    global _recommender
    if _recommender is None:
        _recommender = OutfitRecommender()
    return _recommender
