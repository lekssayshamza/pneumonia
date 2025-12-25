"""
Script to help organize chest X-ray data into the correct structure
"""
import os
import shutil
from pathlib import Path
import random
from sklearn.model_selection import train_test_split

def organize_data(source_dir, target_dir='data', train_split=0.8, random_seed=42):
    """
    Organize chest X-ray images into train/val/test structure.
    
    Expected source structure:
    source_dir/
        NORMAL/
            image1.jpg
            image2.jpg
            ...
        PNEUMONIA/
            image1.jpg
            image2.jpg
            ...
    
    Creates target structure:
    target_dir/
        train/
            NORMAL/
            PNEUMONIA/
        val/
            NORMAL/
            PNEUMONIA/
        test/
            NORMAL/
            PNEUMONIA/
    
    Args:
        source_dir: Source directory with class folders
        target_dir: Target directory for organized data
        train_split: Fraction for training (rest split equally between val and test)
        random_seed: Random seed for reproducibility
    """
    random.seed(random_seed)
    
    # Create target directories
    for split in ['train', 'val', 'test']:
        for class_name in ['NORMAL', 'PNEUMONIA']:
            os.makedirs(os.path.join(target_dir, split, class_name), exist_ok=True)
    
    # Process each class
    for class_name in ['NORMAL', 'PNEUMONIA']:
        source_class_dir = os.path.join(source_dir, class_name)
        
        if not os.path.exists(source_class_dir):
            print(f"Warning: {source_class_dir} not found, skipping...")
            continue
        
        # Get all image files
        image_files = [f for f in os.listdir(source_class_dir)
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.jfif'))]
        
        if len(image_files) == 0:
            print(f"Warning: No images found in {source_class_dir}")
            continue
        
        print(f"\nProcessing {class_name}: {len(image_files)} images")
        
        # Split: 80% train, 10% val, 10% test
        train_files, temp_files = train_test_split(
            image_files, test_size=(1 - train_split), random_state=random_seed
        )
        val_files, test_files = train_test_split(
            temp_files, test_size=0.5, random_state=random_seed
        )
        
        # Copy files to respective directories
        splits = {
            'train': train_files,
            'val': val_files,
            'test': test_files
        }
        
        for split_name, files in splits.items():
            target_split_dir = os.path.join(target_dir, split_name, class_name)
            print(f"  {split_name}: {len(files)} images")
            
            for img_file in files:
                source_path = os.path.join(source_class_dir, img_file)
                target_path = os.path.join(target_split_dir, img_file)
                
                try:
                    shutil.copy2(source_path, target_path)
                except Exception as e:
                    print(f"    Error copying {img_file}: {e}")
    
    print(f"\n[OK] Data organization complete!")
    print(f"  Organized data saved to: {target_dir}/")


def check_data_structure(data_dir):
    """
    Check and display the structure of the data directory.
    """
    print(f"\nChecking data structure in: {data_dir}\n")
    
    if not os.path.exists(data_dir):
        print(f"[X] Directory '{data_dir}' does not exist!")
        return False
    
    # Check for class-based structure
    class_dirs = ['NORMAL', 'PNEUMONIA']
    found_classes = []
    
    for class_name in class_dirs:
        class_path = os.path.join(data_dir, class_name)
        if os.path.exists(class_path):
            images = [f for f in os.listdir(class_path)
                     if f.lower().endswith(('.png', '.jpg', '.jpeg', '.jfif'))]
            found_classes.append(class_name)
            print(f"[OK] {class_name}: {len(images)} images")
        else:
            print(f"[X] {class_name}: directory not found")
    
    # Check for train/val structure
    train_dir = os.path.join(data_dir, 'train')
    val_dir = os.path.join(data_dir, 'val')
    
    if os.path.exists(train_dir) and os.path.exists(val_dir):
        print("\n[OK] Train/Val structure found:")
        for split in ['train', 'val']:
            split_dir = os.path.join(data_dir, split)
            print(f"\n  {split.upper()}:")
            for class_name in class_dirs:
                class_path = os.path.join(split_dir, class_name)
                if os.path.exists(class_path):
                    images = [f for f in os.listdir(class_path)
                             if f.lower().endswith(('.png', '.jpg', '.jpeg', '.jfif'))]
                    print(f"    {class_name}: {len(images)} images")
    
    if len(found_classes) == 2:
        print("\n[OK] Valid structure for training!")
        return True
    else:
        print("\n[X] Invalid structure. Expected:")
        print("  data_dir/")
        print("    NORMAL/")
        print("    PNEUMONIA/")
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Organize chest X-ray data')
    parser.add_argument('--source', type=str, required=True,
                       help='Source directory with NORMAL and PNEUMONIA folders')
    parser.add_argument('--target', type=str, default='data',
                       help='Target directory for organized data (default: data)')
    parser.add_argument('--train_split', type=float, default=0.8,
                       help='Fraction for training set (default: 0.8)')
    parser.add_argument('--check', action='store_true',
                       help='Only check data structure without organizing')
    
    args = parser.parse_args()
    
    if args.check:
        check_data_structure(args.source)
    else:
        if not os.path.exists(args.source):
            print(f"Error: Source directory '{args.source}' does not exist!")
            return
        
        check_data_structure(args.source)
        
        response = input(f"\nOrganize data from '{args.source}' to '{args.target}'? (y/n): ")
        if response.lower() == 'y':
            organize_data(args.source, args.target, args.train_split)
        else:
            print("Cancelled.")


if __name__ == '__main__':
    main()

