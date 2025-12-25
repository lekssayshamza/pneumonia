"""
Script to train the pneumonia detection model
"""
import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from sklearn.model_selection import train_test_split
import argparse

def create_model(input_shape=(224, 224, 3)):
    """
    Create a CNN model for pneumonia detection.
    Using a simple but effective architecture.
    """
    model = models.Sequential([
        # Convolutional blocks
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        layers.MaxPooling2D(2, 2),
        
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D(2, 2),
        
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D(2, 2),
        
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.MaxPooling2D(2, 2),
        
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.MaxPooling2D(2, 2),
        
        # Fully connected layers
        layers.Flatten(),
        layers.Dropout(0.5),
        layers.Dense(512, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(1, activation='sigmoid')  # Binary classification
    ])
    
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy', 'precision', 'recall']
    )
    
    return model


def create_model_v2(input_shape=(224, 224, 3)):
    """
    Alternative model using transfer learning (smaller, faster training).
    """
    base_model = keras.applications.MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = True
    
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.5),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.0001),
        loss='binary_crossentropy',
        metrics=['accuracy', 'precision', 'recall']
    )
    
    return model


def train_with_generator(data_dir, epochs=20, batch_size=32, validation_split=0.2, model_type='simple'):
    """
    Train model using ImageDataGenerator (good for large datasets).
    
    Expected directory structure:
    data_dir/
        train/
            NORMAL/
            PNEUMONIA/
        val/
            NORMAL/
            PNEUMONIA/
    
    OR single directory:
    data_dir/
        NORMAL/
        PNEUMONIA/
    """
    # Check if train/val directories exist, otherwise use single directory
    train_dir = os.path.join(data_dir, 'train')
    val_dir = os.path.join(data_dir, 'val')
    
    if os.path.exists(train_dir) and os.path.exists(val_dir):
        # Use separate train/val directories
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,
            zoom_range=0.2,
            fill_mode='nearest',
            # Handle class imbalance with class_weight or use balanced sampling
            # We'll handle this in the model fit with class_weight
        )
        
        val_datagen = ImageDataGenerator(rescale=1./255)
        
        train_generator = train_datagen.flow_from_directory(
            train_dir,
            target_size=(224, 224),
            batch_size=batch_size,
            class_mode='binary',
            shuffle=True
        )
        
        val_generator = val_datagen.flow_from_directory(
            val_dir,
            target_size=(224, 224),
            batch_size=batch_size,
            class_mode='binary',
            shuffle=False
        )
        
        steps_per_epoch = train_generator.samples // batch_size
        validation_steps = val_generator.samples // batch_size
        
    else:
        # Use single directory with validation split
        datagen = ImageDataGenerator(
            rescale=1./255,
            validation_split=validation_split,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,
            zoom_range=0.2,
            fill_mode='nearest'
        )
        
        train_generator = datagen.flow_from_directory(
            data_dir,
            target_size=(224, 224),
            batch_size=batch_size,
            class_mode='binary',
            subset='training',
            shuffle=True
        )
        
        val_generator = datagen.flow_from_directory(
            data_dir,
            target_size=(224, 224),
            batch_size=batch_size,
            class_mode='binary',
            subset='validation',
            shuffle=False
        )
        
        steps_per_epoch = train_generator.samples // batch_size
        validation_steps = val_generator.samples // batch_size
    
    print(f"\nClasses found: {train_generator.class_indices}")
    print(f"Training samples: {train_generator.samples}")
    print(f"Validation samples: {val_generator.samples}")
    
    # Calculate class weights to handle imbalance
    class_indices = train_generator.class_indices
    class_counts = {}
    
    # Determine the correct directory to count from
    if os.path.exists(train_dir):
        count_dir = train_dir
    else:
        count_dir = data_dir
    
    # Count samples per class
    for class_name, class_idx in class_indices.items():
        class_path = os.path.join(count_dir, class_name)
        if os.path.exists(class_path):
            images = [f for f in os.listdir(class_path)
                     if f.lower().endswith(('.png', '.jpg', '.jpeg', '.jfif'))]
            class_counts[class_idx] = len(images)
        else:
            class_counts[class_idx] = 0
    
    # Calculate weights (inverse frequency) to balance classes
    if len(class_counts) > 0 and max(class_counts.values()) > 0:
        max_count = max(class_counts.values())
        class_weight = {idx: max_count / count if count > 0 else 1.0 
                       for idx, count in class_counts.items()}
    else:
        class_weight = None
    
    print(f"\nClass distribution:")
    for class_name, class_idx in class_indices.items():
        print(f"  {class_name} (idx {class_idx}): {class_counts.get(class_idx, 0)} samples")
    if class_weight:
        print(f"\nClass weights for balancing: {class_weight}")
    else:
        print("\n[Warning] Could not calculate class weights, training without balancing")
    
    # Create model
    if model_type == 'simple':
        model = create_model()
    elif model_type == 'transfer':
        model = create_model_v2()
    else:
        raise ValueError(f"Unknown model type: {model_type}. Use 'simple' or 'transfer'")
    
    model.summary()
    
    # Callbacks
    callbacks = [
        ModelCheckpoint(
            'models/pneumonia_model.h5',
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=1
        )
    ]
    
    # Train with class weights to handle imbalance
    fit_kwargs = {
        'steps_per_epoch': steps_per_epoch,
        'epochs': epochs,
        'validation_data': val_generator,
        'validation_steps': validation_steps,
        'callbacks': callbacks,
        'verbose': 1
    }
    
    # Add class_weight only if it was calculated
    if class_weight:
        fit_kwargs['class_weight'] = class_weight
    
    history = model.fit(train_generator, **fit_kwargs)
    
    print("\nTraining completed!")
    print(f"Best model saved to: models/pneumonia_model.h5")
    
    return model, history


def main():
    parser = argparse.ArgumentParser(description='Train pneumonia detection model')
    parser.add_argument('--data_dir', type=str, default='data',
                       help='Path to data directory (default: data)')
    parser.add_argument('--epochs', type=int, default=20,
                       help='Number of training epochs (default: 20)')
    parser.add_argument('--batch_size', type=int, default=32,
                       help='Batch size (default: 32)')
    parser.add_argument('--validation_split', type=float, default=0.2,
                       help='Validation split ratio (default: 0.2)')
    parser.add_argument('--model_type', type=str, default='simple',
                       choices=['simple', 'transfer'],
                       help='Model type: simple or transfer learning (default: simple)')
    
    args = parser.parse_args()
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Check if data directory exists
    if not os.path.exists(args.data_dir):
        print(f"Error: Data directory '{args.data_dir}' not found!")
        print("\nExpected structure:")
        print("  Option 1 (single directory):")
        print("    data_dir/")
        print("      NORMAL/")
        print("      PNEUMONIA/")
        print("\n  Option 2 (separate train/val):")
        print("    data_dir/")
        print("      train/")
        print("        NORMAL/")
        print("        PNEUMONIA/")
        print("      val/")
        print("        NORMAL/")
        print("        PNEUMONIA/")
        return
    
    print(f"Starting training with:")
    print(f"  Data directory: {args.data_dir}")
    print(f"  Epochs: {args.epochs}")
    print(f"  Batch size: {args.batch_size}")
    print(f"  Model type: {args.model_type}")
    
    train_with_generator(
        args.data_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        validation_split=args.validation_split,
        model_type=args.model_type
    )


if __name__ == '__main__':
    main()

