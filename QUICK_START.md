# Guide Rapide - Démarrage

## ✅ Vérification Complète

Tout est prêt ! Votre projet contient :
- **5,856 images** au total
  - Train : 5,216 images (1,341 NORMAL, 3,875 PNEUMONIA)
  - Val : 16 images (8 NORMAL, 8 PNEUMONIA)
  - Test : 624 images (234 NORMAL, 390 PNEUMONIA)
- Toutes les dépendances installées
- Un modèle existant trouvé

## 🚀 Entraîner le Modèle

### Option 1 : Modèle Simple (Plus Rapide - Recommandé pour débuter)

```bash
python train_model.py --data_dir data/chest_xray --epochs 20 --batch_size 32 --model_type simple
```

### Option 2 : Modèle avec Transfer Learning (Plus Performant)

```bash
python train_model.py --data_dir data/chest_xray --epochs 15 --batch_size 16 --model_type transfer
```

### Options Avancées

```bash
# Avec plus d'époques
python train_model.py --data_dir data/chest_xray --epochs 30 --batch_size 32 --model_type simple

# Batch size plus petit si vous avez peu de mémoire
python train_model.py --data_dir data/chest_xray --epochs 20 --batch_size 16 --model_type simple
```

## 📊 Pendant l'Entraînement

- Le meilleur modèle sera automatiquement sauvegardé dans `models/pneumonia_model.h5`
- L'entraînement s'arrêtera automatiquement si la validation ne s'améliore plus (Early Stopping)
- Le taux d'apprentissage sera réduit automatiquement si nécessaire

## 🔍 Vérifier l'État du Projet

```bash
python check_setup.py
```

## 🏃 Utiliser le Modèle Entraîné

Une fois l'entraînement terminé, le modèle sera automatiquement utilisé par l'application :

```bash
streamlit run app.py
```

## ⚠️ Notes Importantes

1. **Déséquilibre des classes** : Vous avez plus d'images PNEUMONIA que NORMAL. Le modèle gère cela automatiquement avec des techniques de balancing.

2. **Validation set petit** : Le set de validation est très petit (16 images). Le modèle utilisera principalement le set de test pour évaluation.

3. **Durée d'entraînement** : 
   - Modèle simple : ~30-60 minutes sur CPU, ~5-10 minutes sur GPU
   - Modèle transfer learning : ~1-2 heures sur CPU, ~15-30 minutes sur GPU

4. **Mémoire** : Si vous rencontrez des erreurs de mémoire, réduisez le `batch_size` (ex: 16 ou 8)

## 📝 Commandes Utiles

```bash
# Vérifier la structure des données
python organize_data.py --check --source data/chest_xray

# Vérifier tout le setup
python check_setup.py

# Entraîner le modèle
python train_model.py --data_dir data/chest_xray --epochs 20 --batch_size 32

# Lancer l'application
streamlit run app.py
```

## 🆘 En cas de Problème

1. **Erreur de mémoire** : Réduisez `--batch_size` à 16 ou 8
2. **Erreur de données** : Vérifiez avec `python check_setup.py`
3. **Le modèle ne s'améliore pas** : Normal, le modèle existant peut déjà être bon. Vous pouvez continuer l'entraînement avec plus d'époques.

