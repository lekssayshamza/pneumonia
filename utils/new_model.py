from PIL import Image, ImageEnhance
import numpy as np
from tensorflow.keras.models import load_model as keras_load_model

# Load the real model
def load_model():
    """
    Load the trained pneumonia detection model from H5 file.
    Returns:
        model: Keras model object
    Raises:
        FileNotFoundError: If model file doesn't exist
        Exception: If model loading fails
    """
    import os
    model_path = "models/pneumonia_model.h5"
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model file not found at {model_path}. "
            "Please ensure pneumonia_model.h5 exists in the models/ directory."
        )
    model = keras_load_model(model_path)
    return model

# Apply a simple heatmap overlay (placeholder for Grad-CAM)
def _apply_heatmap_to_image(pil_img, heatmap, alpha=0.5):
    w, h = pil_img.size
    hm = (np.clip(heatmap, 0, 1) * 255).astype(np.uint8)
    hm_img = Image.fromarray(hm).resize((w, h)).convert("L")
    red = Image.new("RGBA", (w, h), (255, 0, 0, 0))
    red_mask = Image.new("L", (w, h))
    red_mask.paste(hm_img)
    red.putalpha(red_mask)
    base = pil_img.convert("RGBA")
    blended = Image.alpha_composite(base, Image.blend(base, red, alpha))
    enhancer = ImageEnhance.Brightness(blended.convert("RGB"))
    return enhancer.enhance(1.05)

# Predict function for the real model
def predict(image_pil, model):
    # Resize and normalize image
    img = image_pil.resize((224, 224))
    x = np.array(img)/255.0
    x = x[np.newaxis, ...]  # batch dimension

    # Real prediction (verbose=0 to suppress warnings in Streamlit)
    prob = float(model.predict(x, verbose=0)[0][0])
    label = "Pneumonia" if prob > 0.5 else "Normal"

    # Placeholder Grad-CAM (can replace later with real one)
    heatmap = np.zeros((224, 224), dtype=np.float32)
    gradcam_img = _apply_heatmap_to_image(img, heatmap, alpha=0.45)

    return label, prob, gradcam_img
