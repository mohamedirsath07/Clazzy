import mongoose from 'mongoose';

const { Schema } = mongoose;

// User Schema
const userSchema = new Schema({
  firebaseUid: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  email: {
    type: String,
    required: true,
    unique: true
  },
  displayName: String,
  photoURL: String,
  preferences: {
    bodyType: {
      type: String,
      enum: ['slim', 'athletic', 'curvy', 'plus-size'],
      default: null
    },
    stylePreference: [{
      type: String,
      enum: ['casual', 'formal', 'sporty', 'trendy', 'classic', 'bohemian']
    }],
    favoriteColors: [String],
    occasionFrequency: {
      casual: { type: Number, default: 0 },
      formal: { type: Number, default: 0 },
      business: { type: Number, default: 0 },
      party: { type: Number, default: 0 },
      date: { type: Number, default: 0 },
      sports: { type: Number, default: 0 }
    }
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  lastLoginAt: Date,
  totalUploads: {
    type: Number,
    default: 0
  },
  totalOutfitsGenerated: {
    type: Number,
    default: 0
  }
});

// Clothing Item Schema
const clothingItemSchema = new Schema({
  userId: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },
  firebaseUid: {
    type: String,
    required: true,
    index: true
  },
  filename: {
    type: String,
    required: true
  },
  type: {
    type: String,
    required: true,
    enum: ['top', 'bottom', 'dress', 'shoes', 'blazer', 'other'],
    index: true
  },
  category: String,
  dominantColor: {
    type: String,
    required: true
  },
  colors: [{
    hex: String,
    rgb: [Number],
    hsv: [Number],
    percentage: Number
  }],
  imageUrl: String,
  thumbnailUrl: String,
  confidence: {
    type: Number,
    min: 0,
    max: 100
  },
  mlEmbedding: [Number], // ResNet50 feature vector
  tags: [String],
  brand: String,
  season: {
    type: String,
    enum: ['spring', 'summer', 'fall', 'winter', 'all-season']
  },
  isFavorite: {
    type: Boolean,
    default: false
  },
  timesWorn: {
    type: Number,
    default: 0
  },
  uploadedAt: {
    type: Date,
    default: Date.now
  },
  lastWornAt: Date
});

// Index for efficient queries
clothingItemSchema.index({ userId: 1, type: 1 });
clothingItemSchema.index({ userId: 1, dominantColor: 1 });
clothingItemSchema.index({ userId: 1, isFavorite: 1 });

// Outfit Schema
const outfitSchema = new Schema({
  userId: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },
  firebaseUid: {
    type: String,
    required: true,
    index: true
  },
  name: String,
  occasion: {
    type: String,
    required: true,
    enum: ['casual', 'formal', 'business', 'party', 'date', 'sports'],
    index: true
  },
  items: [{
    itemId: {
      type: Schema.Types.ObjectId,
      ref: 'ClothingItem'
    },
    filename: String,
    type: String,
    color: String,
    imageUrl: String
  }],
  score: {
    type: Number,
    min: 0,
    max: 100
  },
  harmonyScore: Number,
  styleScore: Number,
  occasionScore: Number,
  isFavorite: {
    type: Boolean,
    default: false
  },
  timesWorn: {
    type: Number,
    default: 0
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  lastWornAt: Date
});

// Index for efficient queries
outfitSchema.index({ userId: 1, occasion: 1 });
outfitSchema.index({ userId: 1, isFavorite: 1 });

// User Activity Schema (Analytics)
const userActivitySchema = new Schema({
  userId: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },
  firebaseUid: {
    type: String,
    required: true,
    index: true
  },
  action: {
    type: String,
    required: true,
    enum: [
      'upload_item',
      'delete_item',
      'generate_outfit',
      'save_outfit',
      'favorite_item',
      'favorite_outfit',
      'wear_outfit',
      'search',
      'filter'
    ],
    index: true
  },
  metadata: Schema.Types.Mixed, // Flexible JSON data
  timestamp: {
    type: Date,
    default: Date.now
  }
});

// TTL Index - automatically delete activities older than 90 days
userActivitySchema.index({ timestamp: 1 }, { expireAfterSeconds: 7776000 }); // 90 days

// Create Models
export const User = mongoose.model('User', userSchema);
export const ClothingItem = mongoose.model('ClothingItem', clothingItemSchema);
export const Outfit = mongoose.model('Outfit', outfitSchema);
export const UserActivity = mongoose.model('UserActivity', userActivitySchema);
