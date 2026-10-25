import pytest
from emergency_recommender import emergency_generate_outfits, _looks_like_top, _looks_like_bottom

def test_looks_like_top():
    assert _looks_like_top("blue_shirt.jpg") is True
    assert _looks_like_top("cotton_tshirt.png") is True
    assert _looks_like_top("formal_blouse.jpg") is True
    assert _looks_like_top("blue_jeans.jpg") is False

def test_looks_like_bottom():
    assert _looks_like_bottom("black_jeans.jpg") is True
    assert _looks_like_bottom("formal_trousers.png") is True
    assert _looks_like_bottom("denim_pant.jpg") is True
    assert _looks_like_bottom("white_shirt.jpg") is False

def test_emergency_generate_outfits_empty():
    assert emergency_generate_outfits([]) == []
    assert emergency_generate_outfits([{"name": "only_one_shirt"}]) == []

def test_emergency_generate_outfits_pairing():
    garments = [
        {"name": "casual_shirt.jpg", "hex": "#ffffff", "color": "White"},
        {"name": "dark_jeans.jpg", "hex": "#000000", "color": "Black"},
    ]
    outfits = emergency_generate_outfits(garments, occasion="casual", max_outfits=3)
    assert len(outfits) == 1
    assert outfits[0]["top"]["role"] == "top"
    assert outfits[0]["bottom"]["role"] == "bottom"
    assert outfits[0]["score"] > 0
