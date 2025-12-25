"""
Preprocessing utilities for chest X-ray images
"""
from PIL import Image
import numpy as np
import os

def preprocess_image(image_path, target_size=(224, 224)):
    """
    Preprocess a single image for model input.
    
    Args:
        image_path: Path to the image file
        target_size: Target size (width, height), default (224, 224)
    
    Returns:
        Preprocessed image as numpy array (normalized to 0-1)
    """
    try:
        img = Image.open(image_path).convert('RGB')
        img = img.resize(target_size)
        img_array = np.array(img) / 255.0  # Normalize to [0, 1]
        return img_array
    except Exception as e:
        raise ValueError(f"Error preprocessing image {image_path}: {str(e)}")


def prepare_dataset(data_dir, target_size=(224, 224)):
    """
    Prepare dataset from directory structure:
    data_dir/
        NORMAL/
            image1.jpg
            image2.jpg
            ...
        PNEUMONIA/
            image1.jpg
            image2.jpg
            ...
    
    Args:
        data_dir: Root directory containing class folders
        target_size: Target image size (width, height)
    
    Returns:
        X: numpy array of images
        y: numpy array of labels (0=Normal, 1=Pneumonia)
        class_names: list of class names
    """
    X = []
    y = []
    class_names = ['NORMAL', 'PNEUMONIA']
    
    for class_idx, class_name in enumerate(class_names):
        class_dir = os.path.join(data_dir, class_name)
        if not os.path.exists(class_dir):
            print(f"Warning: Directory {class_dir} does not exist, skipping...")
            continue
        
        image_files = [f for f in os.listdir(class_dir) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        print(f"Loading {len(image_files)} images from {class_name}...")
        
        for img_file in image_files:
            img_path = os.path.join(class_dir, img_file)
            try:
                img_array = preprocess_image(img_path, target_size)
                X.append(img_array)
                y.append(class_idx)
            except Exception as e:
                print(f"Error loading {img_path}: {e}")
                continue
    
    X = np.array(X)
    y = np.array(y)
    
    print(f"\nDataset prepared:")
    print(f"  Total images: {len(X)}")
    print(f"  Normal: {np.sum(y == 0)}")
    print(f"  Pneumonia: {np.sum(y == 1)}")
    print(f"  Image shape: {X.shape}")
    
    return X, y, class_names


def create_train_val_split(data_dir, val_split=0.2, random_seed=42):
    """
    Create train/validation split from data directory.
    
    Args:
        data_dir: Root directory containing class folders
        val_split: Fraction of data to use for validation (0.0 to 1.0)
        random_seed: Random seed for reproducibility
    
    Returns:
        (X_train, y_train, X_val, y_val, class_names)
    """
    from sklearn.model_selection import train_test_split
    
    X, y, class_names = prepare_dataset(data_dir)
    
    if val_split > 0:
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=val_split, random_state=random_seed, stratify=y
        )
        print(f"\nTrain/Val split:")
        print(f"  Train: {len(X_train)} images")
        print(f"  Val: {len(X_val)} images")
        return X_train, y_train, X_val, y_val, class_names
    else:
        return X, y, None, None, class_names

