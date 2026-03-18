import express from 'express';
import { User, ClothingItem, Outfit, UserActivity } from './models';

const router = express.Router();

// ===========================
// USER ROUTES
// ===========================

// Create or get user
router.post('/api/users', async (req, res) => {
  try {
    const { firebaseUid, email, displayName, photoURL } = req.body;

    let user = await User.findOne({ firebaseUid });

    if (!user) {
      user = await User.create({
        firebaseUid,
        email,
        displayName,
        photoURL,
        lastLoginAt: new Date()
      });
      console.log(`✅ New user created: ${email}`);
    } else {
      user.lastLoginAt = new Date();
      await user.save();
    }

    res.json(user);
  } catch (error) {
    console.error('Error creating/getting user:', error);
    res.status(500).json({ error: 'Failed to create/get user' });
  }
});

// Get user profile
router.get('/api/users/:firebaseUid', async (req, res) => {
  try {
    const user = await User.findOne({ firebaseUid: req.params.firebaseUid });
    
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json(user);
  } catch (error) {
    console.error('Error getting user:', error);
    res.status(500).json({ error: 'Failed to get user' });
  }
});

// Update user preferences
router.patch('/api/users/:firebaseUid/preferences', async (req, res) => {
  try {
    const user = await User.findOneAndUpdate(
      { firebaseUid: req.params.firebaseUid },
      { $set: { preferences: req.body } },
      { new: true }
    );

    res.json(user);
  } catch (error) {
    console.error('Error updating preferences:', error);
    res.status(500).json({ error: 'Failed to update preferences' });
  }
});

// ===========================
// WARDROBE ROUTES
// ===========================

// Add clothing item
router.post('/api/wardrobe/items', async (req, res) => {
  try {
    const {
      firebaseUid,
      filename,
      type,
      category,
      dominantColor,
      colors,
      imageUrl,
      confidence,
      mlEmbedding
    } = req.body;

    // Get user
    const user = await User.findOne({ firebaseUid });
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Create clothing item
    const item = await ClothingItem.create({
      userId: user._id,
      firebaseUid,
      filename,
      type,
      category,
      dominantColor,
      colors,
      imageUrl,
      confidence,
      mlEmbedding
    });

    // Update user stats
    await User.findByIdAndUpdate(user._id, {
      $inc: { totalUploads: 1 }
    });

    // Log activity
    await UserActivity.create({
      userId: user._id,
      firebaseUid,
      action: 'upload_item',
      metadata: { itemId: item._id, type, dominantColor }
    });

    console.log(`✅ Item added: ${filename} (${type})`);
    res.json(item);
  } catch (error) {
    console.error('Error adding item:', error);
    res.status(500).json({ error: 'Failed to add item' });
  }
});

// Get all wardrobe items
router.get('/api/wardrobe/items/:firebaseUid', async (req, res) => {
  try {
    const { type, color, favorite, limit } = req.query;
    
    const query: any = { firebaseUid: req.params.firebaseUid };
    
    if (type) query.type = type;
    if (color) query.dominantColor = color;
    if (favorite === 'true') query.isFavorite = true;

    const items = await ClothingItem.find(query)
      .sort({ uploadedAt: -1 })
      .limit(limit ? parseInt(limit as string) : 100);

    res.json(items);
  } catch (error) {
    console.error('Error getting items:', error);
    res.status(500).json({ error: 'Failed to get items' });
  }
});

// Get single item
router.get('/api/wardrobe/items/:firebaseUid/:itemId', async (req, res) => {
  try {
    const item = await ClothingItem.findOne({
      _id: req.params.itemId,
      firebaseUid: req.params.firebaseUid
    });

    if (!item) {
      return res.status(404).json({ error: 'Item not found' });
    }

    res.json(item);
  } catch (error) {
    console.error('Error getting item:', error);
    res.status(500).json({ error: 'Failed to get item' });
  }
});

// Update item (favorite, tags, etc.)
router.patch('/api/wardrobe/items/:itemId', async (req, res) => {
  try {
    const item = await ClothingItem.findByIdAndUpdate(
      req.params.itemId,
      { $set: req.body },
      { new: true }
    );

    res.json(item);
  } catch (error) {
    console.error('Error updating item:', error);
    res.status(500).json({ error: 'Failed to update item' });
  }
});

// Delete item
router.delete('/api/wardrobe/items/:itemId', async (req, res) => {
  try {
    await ClothingItem.findByIdAndDelete(req.params.itemId);
    res.json({ message: 'Item deleted successfully' });
  } catch (error) {
    console.error('Error deleting item:', error);
    res.status(500).json({ error: 'Failed to delete item' });
  }
});

// ===========================
// OUTFIT ROUTES
// ===========================

// Save outfit
router.post('/api/outfits', async (req, res) => {
  try {
    const {
      firebaseUid,
      name,
      occasion,
      items,
      score,
      harmonyScore,
      styleScore,
      occasionScore
    } = req.body;

    console.log(`📥 Saving outfit for user: ${firebaseUid}`);
    console.log(`   Name: ${name || 'Unnamed'}, Occasion: ${occasion}, Items: ${items?.length || 0}`);

    const user = await User.findOne({ firebaseUid });
    if (!user) {
      console.error(`❌ User not found: ${firebaseUid}`);
      return res.status(404).json({ error: 'User not found' });
    }

    const outfit = await Outfit.create({
      userId: user._id,
      firebaseUid,
      name,
      occasion,
      items,
      score,
      harmonyScore,
      styleScore,
      occasionScore
    });

    // Update user stats
    await User.findByIdAndUpdate(user._id, {
      $inc: { 
        totalOutfitsGenerated: 1,
        [`preferences.occasionFrequency.${occasion}`]: 1
      }
    });

    // Log activity
    await UserActivity.create({
      userId: user._id,
      firebaseUid,
      action: 'save_outfit',
      metadata: { outfitId: outfit._id, occasion, score }
    });

    console.log(`✅ Outfit saved successfully! ID: ${outfit._id}`);
    res.json(outfit);
  } catch (error) {
    console.error('❌ Error saving outfit:', error);
    res.status(500).json({ 
      error: 'Failed to save outfit', 
      details: error instanceof Error ? error.message : String(error)
    });
  }
});

// DEBUG: Get ALL outfits (for debugging)
router.get('/api/outfits/debug/all', async (req, res) => {
  try {
    const allOutfits = await Outfit.find({}).sort({ createdAt: -1 });
    res.json({
      total: allOutfits.length,
      outfits: allOutfits
    });
  } catch (error) {
    console.error('Error getting all outfits:', error);
    res.status(500).json({ error: 'Failed to get all outfits' });
  }
});

// Get all outfits
router.get('/api/outfits/:firebaseUid', async (req, res) => {
  try {
    const { occasion, favorite, limit } = req.query;
    
    const query: any = { firebaseUid: req.params.firebaseUid };
    
    if (occasion) query.occasion = occasion;
    if (favorite === 'true') query.isFavorite = true;

    const outfits = await Outfit.find(query)
      .sort({ createdAt: -1 })
      .limit(limit ? parseInt(limit as string) : 50);

    console.log(`📊 Found ${outfits.length} outfits for user ${req.params.firebaseUid}`);
    res.json(outfits);
  } catch (error) {
    console.error('Error getting outfits:', error);
    res.status(500).json({ error: 'Failed to get outfits' });
  }
});

// Get single outfit
router.get('/api/outfits/:firebaseUid/:outfitId', async (req, res) => {
  try {
    const outfit = await Outfit.findOne({
      _id: req.params.outfitId,
      firebaseUid: req.params.firebaseUid
    });

    if (!outfit) {
      return res.status(404).json({ error: 'Outfit not found' });
    }

    res.json(outfit);
  } catch (error) {
    console.error('Error getting outfit:', error);
    res.status(500).json({ error: 'Failed to get outfit' });
  }
});

// Update outfit
router.patch('/api/outfits/:outfitId', async (req, res) => {
  try {
    const outfit = await Outfit.findByIdAndUpdate(
      req.params.outfitId,
      { $set: req.body },
      { new: true }
    );

    res.json(outfit);
  } catch (error) {
    console.error('Error updating outfit:', error);
    res.status(500).json({ error: 'Failed to update outfit' });
  }
});

// Delete outfit
router.delete('/api/outfits/:outfitId', async (req, res) => {
  try {
    await Outfit.findByIdAndDelete(req.params.outfitId);
    res.json({ message: 'Outfit deleted successfully' });
  } catch (error) {
    console.error('Error deleting outfit:', error);
    res.status(500).json({ error: 'Failed to delete outfit' });
  }
});

// ===========================
// ANALYTICS ROUTES
// ===========================

// Get user analytics
router.get('/api/analytics/:firebaseUid', async (req, res) => {
  try {
    const user = await User.findOne({ firebaseUid: req.params.firebaseUid });
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Get item stats
    const itemsByType = await ClothingItem.aggregate([
      { $match: { userId: user._id } },
      { $group: { _id: '$type', count: { $sum: 1 } } }
    ]);

    const itemsByColor = await ClothingItem.aggregate([
      { $match: { userId: user._id } },
      { $group: { _id: '$dominantColor', count: { $sum: 1 } } },
      { $sort: { count: -1 } },
      { $limit: 5 }
    ]);

    // Get outfit stats
    const outfitsByOccasion = await Outfit.aggregate([
      { $match: { userId: user._id } },
      { $group: { _id: '$occasion', count: { $sum: 1 } } }
    ]);

    // Recent activity
    const recentActivity = await UserActivity.find({ userId: user._id })
      .sort({ timestamp: -1 })
      .limit(20);

    res.json({
      user: {
        totalUploads: user.totalUploads,
        totalOutfitsGenerated: user.totalOutfitsGenerated,
        occasionFrequency: user.preferences?.occasionFrequency
      },
      items: {
        byType: itemsByType,
        byColor: itemsByColor
      },
      outfits: {
        byOccasion: outfitsByOccasion
      },
      recentActivity
    });
  } catch (error) {
    console.error('Error getting analytics:', error);
    res.status(500).json({ error: 'Failed to get analytics' });
  }
});

// Track activity
router.post('/api/analytics/track', async (req, res) => {
  try {
    const { firebaseUid, action, metadata } = req.body;

    const user = await User.findOne({ firebaseUid });
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    await UserActivity.create({
      userId: user._id,
      firebaseUid,
      action,
      metadata
    });

    res.json({ message: 'Activity tracked' });
  } catch (error) {
    console.error('Error tracking activity:', error);
    res.status(500).json({ error: 'Failed to track activity' });
  }
});

export default router;
