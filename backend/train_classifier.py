"""
Custom Clothing Classifier Training Script
============================================
Train a specialized model to distinguish between:
- Tops (shirts, t-shirts, blouses, sweaters, jackets)
- Bottoms (pants, jeans, shorts, skirts)
- Dresses (full-body garments)
- Shoes (footwear)
- Other

Uses ResNet50 transfer learning with custom training data.
"""

import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
import os
from pathlib import Path
import numpy as np

# Configuration
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 0.0001

# Categories
CATEGORIES = ['top', 'bottom', 'dress', 'shoes', 'other']
NUM_CLASSES = len(CATEGORIES)


def create_model():
    """
    Create a ResNet50-based model for clothing classification
    """
    print("🔨 Building model architecture...")
    
    # Load pre-trained ResNet50 (without top layers)
    base_model = ResNet50(
        weights='imagenet',
        include_top=False,
        input_shape=(IMG_SIZE, IMG_SIZE, 3)
    )
    
    # Freeze early layers, train later layers
    for layer in base_model.layers[:-20]:
        layer.trainable = False
    
    # Add custom classification layers
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.5)(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.3)(x)
    predictions = Dense(NUM_CLASSES, activation='softmax')(x)
    
    # Create final model
    model = Model(inputs=base_model.input, outputs=predictions)
    
    # Compile model
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy', tf.keras.metrics.TopKCategoricalAccuracy(k=2, name='top2_accuracy')]
    )
    
    print(f"✅ Model created with {NUM_CLASSES} classes")
    return model


def setup_data_generators(data_dir: str):
    """
    Setup data generators for training and validation
    
    Expected directory structure:
    data_dir/
        train/
            top/
                image1.jpg
                image2.jpg
                ...
            bottom/
                image1.jpg
                ...
            dress/
            shoes/
            other/
        validation/
            top/
            bottom/
            dress/
            shoes/
            other/
    """
    print("📂 Setting up data generators...")
    
    # Data augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2,
        shear_range=0.2,
        fill_mode='nearest'
    )
    
    # Only rescaling for validation
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    # Load training data
    train_generator = train_datagen.flow_from_directory(
        os.path.join(data_dir, 'train'),
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        classes=CATEGORIES,
        shuffle=True
    )
    
    # Load validation data
    val_generator = val_datagen.flow_from_directory(
        os.path.join(data_dir, 'validation'),
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        classes=CATEGORIES,
        shuffle=False
    )
    
    print(f"✅ Found {train_generator.samples} training images")
    print(f"✅ Found {val_generator.samples} validation images")
    print(f"   Class distribution:")
    for category in CATEGORIES:
        train_count = len([f for f in os.listdir(os.path.join(data_dir, 'train', category))])
        val_count = len([f for f in os.listdir(os.path.join(data_dir, 'validation', category))])
        print(f"      {category}: {train_count} train, {val_count} val")
    
    return train_generator, val_generator


def train_model(data_dir: str, output_dir: str = 'models'):
    """
    Train the clothing classifier model
    
    Args:
        data_dir: Directory containing train/ and validation/ subdirectories
        output_dir: Directory to save trained model
    """
    print("🚀 Starting training process...")
    print(f"   Data directory: {data_dir}")
    print(f"   Output directory: {output_dir}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Setup data
    train_gen, val_gen = setup_data_generators(data_dir)
    
    # Create model
    model = create_model()
    
    # Print model summary
    print("\n📊 Model Summary:")
    model.summary()
    
    # Setup callbacks
    callbacks = [
        # Save best model
        ModelCheckpoint(
            os.path.join(output_dir, 'clothing_classifier_best.h5'),
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        ),
        # Early stopping
        EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        # Reduce learning rate on plateau
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        )
    ]
    
    # Calculate steps
    steps_per_epoch = train_gen.samples // BATCH_SIZE
    validation_steps = val_gen.samples // BATCH_SIZE
    
    print(f"\n🏋️ Training configuration:")
    print(f"   Epochs: {EPOCHS}")
    print(f"   Batch size: {BATCH_SIZE}")
    print(f"   Steps per epoch: {steps_per_epoch}")
    print(f"   Validation steps: {validation_steps}")
    print(f"   Learning rate: {LEARNING_RATE}")
    
    # Train model
    print("\n🎓 Starting training...")
    history = model.fit(
        train_gen,
        steps_per_epoch=steps_per_epoch,
        epochs=EPOCHS,
        validation_data=val_gen,
        validation_steps=validation_steps,
        callbacks=callbacks,
        verbose=1
    )
    
    # Save final model
    final_model_path = os.path.join(output_dir, 'clothing_classifier_final.h5')
    model.save(final_model_path)
    print(f"\n✅ Training complete!")
    print(f"   Final model saved: {final_model_path}")
    print(f"   Best model saved: {os.path.join(output_dir, 'clothing_classifier_best.h5')}")
    
    # Print final metrics
    print(f"\n📈 Final Training Metrics:")
    print(f"   Training Accuracy: {history.history['accuracy'][-1]:.4f}")
    print(f"   Validation Accuracy: {history.history['val_accuracy'][-1]:.4f}")
    print(f"   Training Loss: {history.history['loss'][-1]:.4f}")
    print(f"   Validation Loss: {history.history['val_loss'][-1]:.4f}")
    
    return model, history


def download_fashion_dataset():
    """
    Download and prepare a fashion dataset for training
    Uses Fashion Product Images dataset or similar
    """
    print("📥 Downloading fashion dataset...")
    print("\n⚠️  IMPORTANT: You need to manually prepare your dataset!")
    print("\n📋 Instructions:")
    print("1. Create a 'training_data' directory with this structure:")
    print("   training_data/")
    print("       train/")
    print("           top/        # Add images of shirts, t-shirts, sweaters, etc.")
    print("           bottom/     # Add images of pants, jeans, shorts, skirts")
    print("           dress/      # Add images of dresses")
    print("           shoes/      # Add images of shoes")
    print("           other/      # Add other clothing items")
    print("       validation/")
    print("           top/")
    print("           bottom/")
    print("           dress/")
    print("           shoes/")
    print("           other/")
    print("\n2. Collect images from:")
    print("   - Kaggle Fashion Datasets (https://www.kaggle.com/datasets)")
    print("   - Fashion Product Images Dataset")
    print("   - DeepFashion Dataset")
    print("   - Your own wardrobe photos")
    print("\n3. Recommended: 200-500 images per category (split 80/20 train/val)")
    print("\n4. Run this script again with: python train_classifier.py --train")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train clothing classifier')
    parser.add_argument('--data-dir', type=str, default='training_data',
                        help='Directory containing train/ and validation/ folders')
    parser.add_argument('--output-dir', type=str, default='models',
                        help='Directory to save trained models')
    parser.add_argument('--train', action='store_true',
                        help='Start training (requires prepared dataset)')
    parser.add_argument('--download', action='store_true',
                        help='Show instructions for downloading dataset')
    
    args = parser.parse_args()
    
    if args.download or not args.train:
        download_fashion_dataset()
    
    if args.train:
        # Check if data directory exists
        if not os.path.exists(args.data_dir):
            print(f"\n❌ Error: Data directory '{args.data_dir}' not found!")
            print("Run with --download flag to see setup instructions.")
        else:
            # Start training
            model, history = train_model(args.data_dir, args.output_dir)
            print("\n🎉 All done! You can now use the trained model in ml_classifier.py")
