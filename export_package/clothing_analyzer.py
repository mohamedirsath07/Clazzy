"""
Clothing Analyzer - Complete Outfit Recommendation System
Combines Model 1 (Classification), Model 2 (Color), and Model 3 (Recommendation)

Usage:
    from clothing_analyzer import ClothingAnalyzer
    
    analyzer = ClothingAnalyzer()
    
    # Analyze single image
    result = analyzer.analyze_image("shirt.jpg")
    
    # Analyze folder and get recommendations
    wardrobe = analyzer.analyze_folder("wardrobe/")
    recommendations = analyzer.recommend_outfits(wardrobe, occasion="formal")
"""

import os
import tensorflow as tf
from color_extraction import extract_dominant_color
from outfit_recommendation import recommend_outfits as get_recommendations


class ClothingAnalyzer:
    """Complete clothing analysis and outfit recommendation system."""
    
    def __init__(self, model_path=None):
        """
        Initialize the analyzer with the clothing classifier model.
        
        Args:
            model_path: Path to the .keras model file. If None, looks in current directory.
        """
        if model_path is None:
            # Look for model in current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, "clothing_classifier_model.keras")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at {model_path}. "
                "Please ensure 'clothing_classifier_model.keras' is in the same directory."
            )
        
        # Load the classification model
        self.model = tf.keras.models.load_model(model_path)
        self.class_names = ['bottom', 'top']
        self.img_size = (150, 150)
        
        print(f"Clothing Analyzer initialized successfully!")
        print(f"Model loaded from: {model_path}")
    
    def predict_type(self, image_path):
        """
        Predict clothing type (top/bottom) for an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            tuple: (predicted_type, confidence)
        """
        img = tf.keras.preprocessing.image.load_img(image_path, target_size=self.img_size)
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)
        
        prediction = self.model.predict(img_array, verbose=0)
        predicted_class = self.class_names[int(prediction[0][0] > 0.5)]
        confidence = prediction[0][0] if prediction[0][0] > 0.5 else 1 - prediction[0][0]
        
        return predicted_class, float(confidence)
    
    def extract_color(self, image_path):
        """
        Extract dominant color from an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            tuple: (color_name, hex_code)
        """
        return extract_dominant_color(image_path)
    
    def analyze_image(self, image_path, name=None):
        """
        Complete analysis of a single clothing image.
        
        Args:
            image_path: Path to the image file
            name: Optional name for the garment (defaults to filename)
            
        Returns:
            dict: Garment info with type, color, hex, confidence
        """
        if name is None:
            name = os.path.splitext(os.path.basename(image_path))[0]
            name = name.replace("_", " ").replace("-", " ").title()
        
        # Model 1: Classify type
        garment_type, confidence = self.predict_type(image_path)
        
        # Model 2: Extract color
        color_name, hex_code = self.extract_color(image_path)
        
        return {
            "name": name,
            "type": garment_type,
            "color": color_name,
            "hex": hex_code,
            "confidence": round(confidence * 100, 2),
            "image_path": image_path
        }
    
    def analyze_folder(self, folder_path, extensions=None):
        """
        Analyze all clothing images in a folder.
        
        Args:
            folder_path: Path to the folder containing images
            extensions: List of valid image extensions (default: common image formats)
            
        Returns:
            list: List of garment dictionaries
        """
        if extensions is None:
            extensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']
        
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        
        image_files = [
            f for f in os.listdir(folder_path)
            if os.path.splitext(f)[1].lower() in extensions
        ]
        
        wardrobe = []
        print(f"Analyzing {len(image_files)} images...")
        
        for img_file in sorted(image_files):
            img_path = os.path.join(folder_path, img_file)
            garment = self.analyze_image(img_path)
            wardrobe.append(garment)
            print(f"  {garment['name']:20} | {garment['type']:6} | {garment['color']:12} | {garment['hex']}")
        
        return wardrobe
    
    def recommend_outfits(self, garments, occasion="casual", top_n=5):
        """
        Generate outfit recommendations from a list of garments.
        
        Args:
            garments: List of garment dictionaries (from analyze_image/analyze_folder)
            occasion: One of "formal", "office", "casual", "party", "date", "college"
            top_n: Number of top recommendations to return
            
        Returns:
            list: Ranked outfit recommendations
        """
        recommendations = get_recommendations(garments, occasion=occasion)
        return recommendations[:top_n]
    
    def get_best_outfit(self, garments, occasion="casual"):
        """
        Get the single best outfit recommendation.
        
        Args:
            garments: List of garment dictionaries
            occasion: One of "formal", "office", "casual", "party", "date", "college"
            
        Returns:
            dict: Best outfit recommendation or None if no valid outfits
        """
        recommendations = self.recommend_outfits(garments, occasion, top_n=1)
        return recommendations[0] if recommendations else None


# Convenience function for quick analysis
def analyze_and_recommend(image_folder, occasion="casual", model_path=None):
    """
    Quick function to analyze a folder and get recommendations.
    
    Args:
        image_folder: Path to folder with clothing images
        occasion: Occasion type
        model_path: Optional path to model file
        
    Returns:
        tuple: (wardrobe, recommendations)
    """
    analyzer = ClothingAnalyzer(model_path)
    wardrobe = analyzer.analyze_folder(image_folder)
    recommendations = analyzer.recommend_outfits(wardrobe, occasion)
    return wardrobe, recommendations


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        occasion = sys.argv[2] if len(sys.argv) > 2 else "casual"
        
        print(f"\nAnalyzing folder: {folder_path}")
        print(f"Occasion: {occasion}\n")
        
        wardrobe, recommendations = analyze_and_recommend(folder_path, occasion)
        
        print(f"\n{'='*60}")
        print(f"TOP OUTFIT RECOMMENDATIONS ({occasion.upper()})")
        print('='*60)
        
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"\n{i}. {rec['outfit'][0]} + {rec['outfit'][1]}")
            print(f"   Colors: {rec['colors'][0]} + {rec['colors'][1]}")
            print(f"   Harmony: {rec['harmony']} | Score: {rec['score']}")
    else:
        print("Usage: python clothing_analyzer.py <image_folder> [occasion]")
        print("\nOccasions: formal, office, casual, party, date, college")
        print("\nExample:")
        print("  python clothing_analyzer.py ./wardrobe casual")
