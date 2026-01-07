"""
Example Usage - Clothing Outfit Recommendation System

This script demonstrates how to use the clothing analyzer in your project.
"""

from clothing_analyzer import ClothingAnalyzer

# =============================================================================
# EXAMPLE 1: Analyze a single image
# =============================================================================
print("=" * 60)
print("EXAMPLE 1: Analyze Single Image")
print("=" * 60)

# Initialize the analyzer (loads the model)
analyzer = ClothingAnalyzer()

# Analyze a single clothing image
# result = analyzer.analyze_image("path/to/your/shirt.jpg")
# print(result)

# Example output:
# {
#     "name": "Shirt",
#     "type": "top",
#     "color": "Royal Blue",
#     "hex": "#1f3c88",
#     "confidence": 97.5,
#     "image_path": "path/to/your/shirt.jpg"
# }


# =============================================================================
# EXAMPLE 2: Analyze a folder of images
# =============================================================================
print("\n" + "=" * 60)
print("EXAMPLE 2: Analyze Folder")
print("=" * 60)

# Put your clothing images in a folder and analyze them
# wardrobe = analyzer.analyze_folder("path/to/your/wardrobe/")

# This returns a list of garment dictionaries


# =============================================================================
# EXAMPLE 3: Get outfit recommendations
# =============================================================================
print("\n" + "=" * 60)
print("EXAMPLE 3: Outfit Recommendations")
print("=" * 60)

# Create sample wardrobe manually (or use analyze_folder)
sample_wardrobe = [
    {"name": "Blue Shirt", "type": "top", "color": "Royal Blue", "hex": "#1f3c88"},
    {"name": "Black Jeans", "type": "bottom", "color": "Black", "hex": "#000000"},
    {"name": "Red T-Shirt", "type": "top", "color": "Red", "hex": "#c1121f"},
    {"name": "Khaki Pants", "type": "bottom", "color": "Khaki", "hex": "#c3b091"},
    {"name": "White Shirt", "type": "top", "color": "White", "hex": "#ffffff"},
]

# Get recommendations for different occasions
occasions = ["formal", "casual", "party"]

for occasion in occasions:
    print(f"\n{occasion.upper()} OCCASION - Top 3 Outfits:")
    print("-" * 40)
    
    recommendations = analyzer.recommend_outfits(sample_wardrobe, occasion=occasion, top_n=3)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec['outfit'][0]} + {rec['outfit'][1]}")
        print(f"     {rec['colors'][0]} + {rec['colors'][1]}")
        print(f"     Harmony: {rec['harmony']} | Score: {rec['score']}")


# =============================================================================
# EXAMPLE 4: Get the best outfit for an occasion
# =============================================================================
print("\n" + "=" * 60)
print("EXAMPLE 4: Best Outfit")
print("=" * 60)

best = analyzer.get_best_outfit(sample_wardrobe, occasion="date")
if best:
    print(f"\nBest outfit for a DATE:")
    print(f"  Wear: {best['outfit'][0]} with {best['outfit'][1]}")
    print(f"  Colors: {best['colors'][0]} + {best['colors'][1]}")
    print(f"  Why: {best['harmony']} harmony (Score: {best['score']})")


# =============================================================================
# EXAMPLE 5: Quick one-liner
# =============================================================================
print("\n" + "=" * 60)
print("EXAMPLE 5: Quick One-Liner Usage")
print("=" * 60)

from clothing_analyzer import analyze_and_recommend

# Analyze folder and get recommendations in one line
# wardrobe, recommendations = analyze_and_recommend("./my_clothes/", occasion="office")

print("\nUsage:")
print('  wardrobe, recommendations = analyze_and_recommend("./my_clothes/", "office")')


print("\n" + "=" * 60)
print("DONE! Modify this script for your project.")
print("=" * 60)
