import { describe, it } from 'node:test';
import assert from 'node:assert';
import {
  normalizeType,
  guessTypeFromFilename,
  detectStructuralFeatures,
  validateOutfit,
} from '../outfitRecommender';
import { MLOutfitRecommendation } from '../mlTypes';

describe('Outfit Recommender & Heuristics', () => {
  it('normalizes type aliases properly', () => {
    assert.strictEqual(normalizeType('t-shirt'), 'top');
    assert.strictEqual(normalizeType('shirt'), 'top');
    assert.strictEqual(normalizeType('blouse'), 'top');
    assert.strictEqual(normalizeType('jeans'), 'bottom');
    assert.strictEqual(normalizeType('trousers'), 'bottom');
    assert.strictEqual(normalizeType('cargo_pants'), 'bottom');
  });

  it('guesses top or bottom from filename', () => {
    assert.strictEqual(guessTypeFromFilename('navy_blue_shirt.png'), 'top');
    assert.strictEqual(guessTypeFromFilename('slim_fit_jeans.jpg'), 'bottom');
    assert.strictEqual(guessTypeFromFilename('cotton_hoodie.png'), 'top');
    assert.strictEqual(guessTypeFromFilename('random_image.jpg'), null);
  });

  it('detects structural garment features', () => {
    assert.strictEqual(detectStructuralFeatures('polo_collar_white', ''), 'top');
    assert.strictEqual(detectStructuralFeatures('item1', 'http://cdn/short-sleeve.jpg'), 'top');
    assert.strictEqual(detectStructuralFeatures('belt-loop_chinos', ''), 'bottom');
  });

  it('validates role-locked outfits', () => {
    const validOutfit: MLOutfitRecommendation = {
      top: {
        filename: 'shirt_1.jpg',
        type: 'top',
        category: 'top',
        color: '#ffffff',
        url: 'http://img1',
        role: 'top',
      },
      bottom: {
        filename: 'pant_1.jpg',
        type: 'bottom',
        category: 'bottom',
        color: '#000000',
        url: 'http://img2',
        role: 'bottom',
      },
      items: [],
      score: 0.9,
      total_items: 2,
    };
    assert.strictEqual(validateOutfit(validOutfit), true);

    // Invalid: same filename for top and bottom
    const invalidSameItem = {
      ...validOutfit,
      bottom: { ...validOutfit.bottom, filename: 'shirt_1.jpg' },
    };
    assert.strictEqual(validateOutfit(invalidSameItem), false);
  });
});
