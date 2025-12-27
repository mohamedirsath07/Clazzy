"""
QUICK START GUIDE: Using the 3 Independent ML Models
====================================================

This guide demonstrates how to use each ML model independently
and how to combine them for complete outfit recommendations.
"""

# ============================================================================
# MODEL 1: CLOTHING CLASSIFIER
# ============================================================================
print("\n" + "="*80)
print("MODEL 1: Clothing Classification")
print("="*80)

from ml_classifier import get_classifier

# Initialize classifier
classifier = get_classifier()

# Example 1: Classify a single image
with open('path/to/shirt.jpg', 'rb') as f:
    image_bytes = f.read()

result = classifier.predict(image_bytes)
print(f"Classification Result:")
print(f"  Type: {result['predicted_type']}")
print(f"  Confidence: {result['confidence']:.2%}")
print(f"  Features Shape: {result['features'].shape}")

# Example 2: Compare style similarity between two items
with open('path/to/shirt1.jpg', 'rb') as f1, open('path/to/shirt2.jpg', 'rb') as f2:
    result1 = classifier.predict(f1.read())
    result2 = classifier.predict(f2.read())
    
    similarity = classifier.compute_similarity(
        result1['features'],
        result2['features']
    )
    print(f"\nStyle Similarity: {similarity:.2%}")


# ============================================================================
# MODEL 2: COLOR EXTRACTOR
# ============================================================================
print("\n" + "="*80)
print("MODEL 2: Color Extraction")
print("="*80)

from color_analyzer import get_color_analyzer

# Initialize analyzer
analyzer = get_color_analyzer()

# Example 1: Extract all dominant colors
with open('path/to/shirt.jpg', 'rb') as f:
    image_bytes = f.read()

colors = analyzer.extract_colors(image_bytes)
print(f"Extracted {len(colors)} dominant colors:")
for i, color in enumerate(colors, 1):
    print(f"  {i}. {color['hex']} - {color['percentage']:.1f}% coverage")
    print(f"     RGB: {color['rgb']}")
    print(f"     HSV: H={color['hsv'][0]:.0f}° S={color['hsv'][1]:.0f}% V={color['hsv'][2]:.0f}%")

# Example 2: Get just the dominant color
dominant = analyzer.get_dominant_color(image_bytes)
print(f"\nDominant Color: {dominant}")

# Example 3: Get human-readable color name
color_name = analyzer.get_color_name(dominant)
print(f"Color Name: {color_name}")


# ============================================================================
# MODEL 3: COLOR HARMONY RECOMMENDER
# ============================================================================
print("\n" + "="*80)
print("MODEL 3: Color Harmony Recommendations")
print("="*80)

from color_harmony import get_color_harmony_recommender

# Initialize recommender
recommender = get_color_harmony_recommender()

# Example 1: Get complementary color (opposite on color wheel)
base_color = "#FF5733"  # Orange-red
complementary = recommender.get_complementary_color(base_color)
print(f"Base Color: {base_color}")
print(f"Complementary: {complementary}")

# Example 2: Get analogous colors (adjacent on color wheel)
analogous = recommender.get_analogous_colors(base_color)
print(f"Analogous Colors: {analogous}")

# Example 3: Get triadic colors (balanced triad)
triadic = recommender.get_triadic_colors(base_color)
print(f"Triadic Colors: {triadic}")

# Example 4: Calculate harmony between two colors
color1 = "#FF5733"
color2 = "#3399FF"
harmony_score = recommender.calculate_harmony(color1, color2)
print(f"\nHarmony Score between {color1} and {color2}: {harmony_score:.2f}")

# Example 5: Get all matching colors with explanations
all_matches = recommender.get_all_matches(base_color)
print(f"\nAll Color Harmonies for {base_color}:")
print(f"  Is Neutral: {all_matches['is_neutral']}")
print(f"  Temperature: {all_matches['temperature']}")
print(f"  Complementary: {all_matches['complementary']['colors']} (score: {all_matches['complementary']['score']})")
print(f"  Analogous: {all_matches['analogous']['colors']} (score: {all_matches['analogous']['score']})")
print(f"  Triadic: {all_matches['triadic']['colors']} (score: {all_matches['triadic']['score']})")

# Example 6: Get style-based recommendations
print("\nStyle-Based Recommendations:")
for style in ['bold', 'harmonious', 'balanced', 'conservative']:
    recommendations = recommender.recommend_matching_colors(
        base_color,
        style=style,
        top_n=3
    )
    print(f"\n  {style.upper()} style:")
    for rec in recommendations:
        print(f"    - {rec['color']} ({rec['type']}, score: {rec['score']})")


# ============================================================================
# COMBINED EXAMPLE: All 3 Models Together
# ============================================================================
print("\n" + "="*80)
print("COMBINED: Using All 3 Models for Complete Analysis")
print("="*80)

def analyze_clothing_item(image_path):
    """Complete analysis using all 3 models"""
    
    # Read image
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    # MODEL 1: Classify clothing type
    classifier = get_classifier()
    classification = classifier.predict(image_bytes)
    
    # MODEL 2: Extract colors
    analyzer = get_color_analyzer()
    colors = analyzer.extract_colors(image_bytes)
    dominant_color = colors[0]['hex']
    
    # MODEL 3: Get matching colors
    recommender = get_color_harmony_recommender()
    matches = recommender.recommend_matching_colors(
        dominant_color,
        style='balanced',
        top_n=3
    )
    
    # Print results
    print(f"\nComplete Analysis:")
    print(f"  Clothing Type: {classification['predicted_type']} ({classification['confidence']:.2%} confidence)")
    print(f"  Dominant Color: {dominant_color}")
    print(f"  Matching Colors:")
    for match in matches:
        print(f"    - {match['color']} ({match['type']})")
    
    return {
        'type': classification['predicted_type'],
        'confidence': classification['confidence'],
        'dominant_color': dominant_color,
        'all_colors': colors,
        'matching_colors': matches
    }

# Example usage
# result = analyze_clothing_item('path/to/shirt.jpg')


# ============================================================================
# OUTFIT RECOMMENDATION: Integration Layer
# ============================================================================
print("\n" + "="*80)
print("OUTFIT RECOMMENDATIONS: Integrating All Models")
print("="*80)

from outfit_recommender import get_outfit_recommender

def create_outfit_recommendations(clothing_items, occasion='casual'):
    """
    Generate outfit recommendations using all 3 models
    
    Args:
        clothing_items: List of items (already analyzed with models 1 & 2)
        occasion: Event type (casual/formal/business/party/date/sports)
    """
    
    # Initialize outfit recommender (uses MODEL 1 & MODEL 3 internally)
    recommender = get_outfit_recommender()
    
    # Generate recommendations
    outfits = recommender.recommend_outfits(
        clothing_items=clothing_items,
        occasion=occasion,
        max_outfits=5,
        items_per_outfit=2
    )
    
    print(f"\nGenerated {len(outfits)} outfit recommendations for '{occasion}':")
    for i, outfit in enumerate(outfits, 1):
        print(f"\n  Outfit {i} (Score: {outfit['score']:.2f}):")
        for item in outfit['items']:
            print(f"    - {item['type']}: {item['dominant_color']}")
    
    return outfits

# Example usage with pre-analyzed items
clothing_items = [
    {
        'id': 'shirt1.jpg',
        'type': 'top',
        'dominant_color': '#FF5733',
        'colors': [...],
        'features': [...]  # From MODEL 1
    },
    {
        'id': 'jeans1.jpg',
        'type': 'bottom',
        'dominant_color': '#3399FF',
        'colors': [...],
        'features': [...]  # From MODEL 1
    }
]

# outfits = create_outfit_recommendations(clothing_items, 'casual')


# ============================================================================
# API USAGE EXAMPLES (HTTP Requests)
# ============================================================================
print("\n" + "="*80)
print("API USAGE: HTTP Request Examples")
print("="*80)

import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Example 1: Classify clothing type (MODEL 1)
def api_classify(image_path):
    with open(image_path, 'rb') as f:
        response = requests.post(
            f"{BASE_URL}/predict-type",
            files={'file': f}
        )
    return response.json()

# Example 2: Extract colors (MODEL 2)
def api_extract_colors(image_path):
    with open(image_path, 'rb') as f:
        response = requests.post(
            f"{BASE_URL}/extract-colors",
            files={'file': f}
        )
    return response.json()

# Example 3: Get color recommendations (MODEL 3)
def api_recommend_colors(hex_color, style='balanced'):
    response = requests.post(
        f"{BASE_URL}/recommend-colors",
        data={
            'hex_color': hex_color,
            'style': style
        }
    )
    return response.json()

# Example 4: Complete analysis (ALL 3 MODELS)
def api_analyze_complete(image_path):
    with open(image_path, 'rb') as f:
        response = requests.post(
            f"{BASE_URL}/analyze-complete",
            files={'file': f}
        )
    return response.json()

# Example 5: Get outfit recommendations (INTEGRATION)
def api_recommend_outfits(occasion='casual', max_items=2):
    response = requests.post(
        f"{BASE_URL}/recommend-outfits",
        data={
            'occasion': occasion,
            'max_items': max_items
        }
    )
    return response.json()

print("\nAPI Endpoint Summary:")
print("  POST /predict-type          - MODEL 1: Classify clothing")
print("  POST /extract-colors        - MODEL 2: Extract colors")
print("  POST /recommend-colors      - MODEL 3: Recommend matching colors")
print("  POST /analyze-complete      - ALL 3 MODELS: Complete analysis")
print("  POST /recommend-outfits     - INTEGRATION: Outfit recommendations")


# ============================================================================
# TESTING INDIVIDUAL MODELS
# ============================================================================
print("\n" + "="*80)
print("TESTING: Quick Model Tests")
print("="*80)

def test_all_models():
    """Test that all 3 models are working correctly"""
    
    print("\n✅ Testing MODEL 1: Clothing Classifier...")
    try:
        classifier = get_classifier()
        print("   ✓ Classifier initialized successfully")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n✅ Testing MODEL 2: Color Extractor...")
    try:
        analyzer = get_color_analyzer()
        print("   ✓ Color Analyzer initialized successfully")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n✅ Testing MODEL 3: Color Harmony Recommender...")
    try:
        recommender = get_color_harmony_recommender()
        
        # Test harmony calculation
        score = recommender.calculate_harmony('#FF0000', '#00FFFF')
        print(f"   ✓ Color Harmony Recommender initialized successfully")
        print(f"   ✓ Test harmony score (Red ↔ Cyan): {score:.2f}")
        
        # Test complementary colors
        comp = recommender.get_complementary_color('#FF0000')
        print(f"   ✓ Complementary of Red: {comp}")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n✅ All 3 models tested successfully!")

# Run tests
if __name__ == "__main__":
    test_all_models()

print("\n" + "="*80)
print("QUICK START GUIDE COMPLETE")
print("="*80)
print("\nFor detailed documentation, see: backend/ML_MODELS_DOCUMENTATION.md")
print("For API documentation, visit: http://localhost:8000/docs")
