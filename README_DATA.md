# Guide d'organisation des données pour l'entraînement du modèle

## Structure des données

Pour entraîner le modèle de détection de pneumonie, organisez vos données selon l'une des structures suivantes :

### Option 1 : Structure simple (recommandée pour commencer)

```
data/
├── NORMAL/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
└── PNEUMONIA/
    ├── image1.jpg
    ├── image2.jpg
    └── ...
```

### Option 2 : Structure avec train/val séparés

```
data/
├── train/
│   ├── NORMAL/
│   │   ├── image1.jpg
│   │   └── ...
│   └── PNEUMONIA/
│       ├── image1.jpg
│       └── ...
└── val/
    ├── NORMAL/
    │   ├── image1.jpg
    │   └── ...
    └── PNEUMONIA/
        ├── image1.jpg
        └── ...
```

## Étapes pour ajouter vos données

### 1. Vérifier la structure de vos données

```bash
python organize_data.py --check --source chemin/vers/vos/donnees
```

### 2. Organiser automatiquement vos données

Si vos données sont dans un dossier avec des sous-dossiers `NORMAL` et `PNEUMONIA`, utilisez :

```bash
python organize_data.py --source chemin/vers/vos/donnees --target data
```

Cela créera automatiquement une structure train/val/test (80%/10%/10%).

### 3. Entraîner le modèle

#### Modèle simple (recommandé pour débuter) :

```bash
python train_model.py --data_dir data --epochs 20 --batch_size 32 --model_type simple
```

#### Modèle avec transfer learning (plus performant, mais plus lent) :

```bash
python train_model.py --data_dir data --epochs 20 --batch_size 32 --model_type transfer
```

## Options d'entraînement

```bash
python train_model.py --help
```

Options disponibles :
- `--data_dir` : Chemin vers le dossier de données (défaut: `data`)
- `--epochs` : Nombre d'époques d'entraînement (défaut: 20)
- `--batch_size` : Taille du batch (défaut: 32)
- `--validation_split` : Fraction pour la validation (défaut: 0.2)
- `--model_type` : Type de modèle : `simple` ou `transfer` (défaut: `simple`)

## Exemple complet

```bash
# 1. Organiser les données
python organize_data.py --source C:\Users\pc\chest_xray --target data

# 2. Vérifier la structure
python organize_data.py --check --source data

# 3. Entraîner le modèle
python train_model.py --data_dir data --epochs 30 --batch_size 16 --model_type simple
```

## Formats d'images supportés

- PNG (.png)
- JPEG (.jpg, .jpeg)
- JFIF (.jfif)

## Notes importantes

1. **Balance des classes** : Assurez-vous d'avoir un nombre équilibré d'images NORMAL et PNEUMONIA pour de meilleurs résultats.

2. **Qualité des images** : 
   - Images claires et bien exposées
   - Radiographies frontales du thorax
   - Résolution minimale recommandée : 224x224 pixels

3. **Taille du dataset** : 
   - Minimum recommandé : 200 images par classe
   - Idéal : 1000+ images par classe

4. **Le modèle entraîné sera sauvegardé dans** : `models/pneumonia_model.h5`

5. **Le modèle actuel dans l'application sera remplacé** : Assurez-vous de sauvegarder l'ancien modèle si nécessaire.

## Après l'entraînement

Une fois le modèle entraîné, il sera automatiquement sauvegardé dans `models/pneumonia_model.h5` et sera utilisé par l'application Streamlit lors du prochain démarrage.

Pour tester le modèle :
```bash
streamlit run app.py
```

