"""
Script pour vérifier que tout est prêt pour l'entraînement
"""
import os
import sys

def check_data_structure():
    """Vérifier la structure des données"""
    print("=" * 60)
    print("VERIFICATION DE LA STRUCTURE DES DONNEES")
    print("=" * 60)
    
    data_path = "data/chest_xray"
    
    if not os.path.exists(data_path):
        print(f"[ERREUR] Le dossier '{data_path}' n'existe pas!")
        return False
    
    print(f"[OK] Dossier '{data_path}' trouve")
    
    # Vérifier train/val/test
    splits = ['train', 'val', 'test']
    classes = ['NORMAL', 'PNEUMONIA']
    
    total_images = 0
    
    for split in splits:
        split_path = os.path.join(data_path, split)
        if not os.path.exists(split_path):
            print(f"[ATTENTION] Dossier '{split}' manquant")
            continue
        
        print(f"\n  {split.upper()}:")
        split_total = 0
        
        for class_name in classes:
            class_path = os.path.join(split_path, class_name)
            if not os.path.exists(class_path):
                print(f"    [X] {class_name}: dossier manquant")
                continue
            
            images = [f for f in os.listdir(class_path)
                     if f.lower().endswith(('.png', '.jpg', '.jpeg', '.jfif'))]
            count = len(images)
            split_total += count
            print(f"    [OK] {class_name}: {count} images")
        
        print(f"    Total {split}: {split_total} images")
        total_images += split_total
    
    print(f"\n[OK] Total d'images: {total_images}")
    return True


def check_dependencies():
    """Vérifier que toutes les dépendances sont installées"""
    print("\n" + "=" * 60)
    print("VERIFICATION DES DEPENDANCES")
    print("=" * 60)
    
    required = [
        ('tensorflow', 'TensorFlow'),
        ('numpy', 'NumPy'),
        ('PIL', 'Pillow'),
        ('sklearn', 'scikit-learn'),
        ('streamlit', 'Streamlit'),
    ]
    
    missing = []
    
    for module, name in required:
        try:
            __import__(module)
            print(f"[OK] {name} installe")
        except ImportError:
            print(f"[ERREUR] {name} manquant")
            missing.append(name)
    
    if missing:
        print(f"\n[ACTION REQUISE] Installez les packages manquants:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    return True


def check_model_directory():
    """Vérifier le dossier models"""
    print("\n" + "=" * 60)
    print("VERIFICATION DU DOSSIER MODELS")
    print("=" * 60)
    
    models_dir = "models"
    
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        print(f"[OK] Dossier '{models_dir}' cree")
    else:
        print(f"[OK] Dossier '{models_dir}' existe")
    
    model_file = os.path.join(models_dir, "pneumonia_model.h5")
    if os.path.exists(model_file):
        size_mb = os.path.getsize(model_file) / (1024 * 1024)
        print(f"[OK] Modele existant trouve: {model_file} ({size_mb:.2f} MB)")
    else:
        print(f"[INFO] Aucun modele existant. Un nouveau sera cree lors de l'entrainement.")
    
    return True


def main():
    """Fonction principale"""
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE DU PROJET")
    print("=" * 60 + "\n")
    
    checks = [
        ("Structure des donnees", check_data_structure),
        ("Dependances", check_dependencies),
        ("Dossier models", check_model_directory),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"[ERREUR] Erreur lors de la verification '{name}': {e}")
            results.append((name, False))
    
    # Résumé final
    print("\n" + "=" * 60)
    print("RESUME")
    print("=" * 60)
    
    all_ok = True
    for name, result in results:
        status = "[OK]" if result else "[ERREUR]"
        print(f"{status} {name}")
        if not result:
            all_ok = False
    
    if all_ok:
        print("\n[SUCCES] Tout est pret pour l'entrainement!")
        print("\nPour entrainer le modele, executez:")
        print("  python train_model.py --data_dir data/chest_xray --epochs 20 --batch_size 32")
    else:
        print("\n[ATTENTION] Certaines verifications ont echoue.")
        print("Corrigez les erreurs avant de proceder a l'entrainement.")
        sys.exit(1)


if __name__ == '__main__':
    main()

