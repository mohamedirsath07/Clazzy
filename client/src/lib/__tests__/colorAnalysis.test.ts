import { describe, it } from 'node:test';
import assert from 'node:assert';
import { hexToRgb, rgbToHsl, calculateColorHarmony, getScoreColor, formatMatchScore } from '../colorAnalysis';

describe('Color Analysis & Harmony Engine', () => {
  it('converts hex to RGB accurately', () => {
    const white = hexToRgb('#ffffff');
    assert.deepStrictEqual(white, { r: 255, g: 255, b: 255 });

    const red = hexToRgb('#ff0000');
    assert.deepStrictEqual(red, { r: 255, g: 0, b: 0 });

    const dark = hexToRgb('#000000');
    assert.deepStrictEqual(dark, { r: 0, g: 0, b: 0 });
  });

  it('converts RGB to HSL accurately', () => {
    const hslRed = rgbToHsl(255, 0, 0);
    assert.strictEqual(hslRed.h, 0);
    assert.strictEqual(hslRed.s, 1);
    assert.strictEqual(hslRed.l, 0.5);

    const hslBlue = rgbToHsl(0, 0, 255);
    assert.strictEqual(hslBlue.h, 240);
  });

  it('calculates high harmony score for complementary colors', () => {
    // Red (#ff0000, 0 deg) and Cyan (#00ffff, 180 deg) are complementary
    const score = calculateColorHarmony('#ff0000', '#00ffff');
    assert.ok(score >= 0.9, `Expected score >= 0.9, got ${score}`);
  });

  it('handles neutral pairings gracefully', () => {
    // Black (#000000) and Navy (#001f3f)
    const score = calculateColorHarmony('#111111', '#001f3f');
    assert.ok(score >= 0.8, `Expected score >= 0.8, got ${score}`);
  });

  it('formats scores correctly', () => {
    assert.strictEqual(formatMatchScore(0.954), '95%');
    assert.strictEqual(formatMatchScore(0.8), '80%');
    assert.strictEqual(getScoreColor(0.9), 'text-emerald-500');
  });
});
