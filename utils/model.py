# utils/model.py
from PIL import Image, ImageFilter, ImageChops, ImageEnhance
import numpy as np
import random
import io

def load_model():
    """
    Mock model loader. In the real project you'll load your trained weights here.
    We keep the interface the same: returns a model-like object (here just a dict).
    """
    return {"name": "mock-model-v1"}

def _random_heatmap(size):
    """
    Create a random soft heatmap (numpy float32, 0..1) with one gaussian blob.
    """
    w, h = size
    x0 = random.uniform(0.3, 0.7) * w
    y0 = random.uniform(0.3, 0.7) * h
    xs = np.linspace(0, w - 1, w)
    ys = np.linspace(0, h - 1, h)
    xv, yv = np.meshgrid(xs, ys)
    sigma = min(w, h) * random.uniform(0.08, 0.18)
    blob = np.exp(-((xv - x0) ** 2 + (yv - y0) ** 2) / (2 * sigma ** 2))
    blob = blob / blob.max()
    return blob.astype(np.float32)

def _apply_heatmap_to_image(pil_img, heatmap, alpha=0.5):
    """
    Overlay a heatmap (0..1) on top of a PIL RGB image and return a new PIL image.
    """
    # ensure sizes
    w, h = pil_img.size
    # convert heatmap to RGBA red overlay
    hm = (np.clip(heatmap, 0, 1) * 255).astype(np.uint8)
    hm_img = Image.fromarray(hm).resize((w, h)).convert("L")

    # create red image
    red = Image.new("RGBA", (w, h), (255, 0, 0, 0))
    red_mask = Image.new("L", (w, h))
    red_mask.paste(hm_img)
    red.putalpha(red_mask)

    base = pil_img.convert("RGBA")

    # blend base and red overlay
    blended = Image.alpha_composite(base, Image.blend(base, red, alpha))
    # lighten a bit for visibility
    enhancer = ImageEnhance.Brightness(blended.convert("RGB"))
    return enhancer.enhance(1.05)

def predict(image_pil, model=None):
    """
    Mock predict function.
    Args:
      image_pil: PIL.Image (RGB)
      model: unused for now
    Returns:
      label (str), prob (float in 0..1), gradcam_pil (PIL.Image)
    """
    # fake probability: slightly higher chance for pneumonia if image is dark
    gray = image_pil.convert("L")
    mean = np.array(gray).mean() / 255.0
    # darker images -> slightly higher pneumonia prob (totally arbitrary)
    prob = 0.4 + (1.0 - mean) * 0.5
    prob = min(max(prob + random.uniform(-0.08, 0.08), 0.01), 0.99)

    label = "Pneumonia" if prob > 0.5 else "Normal"

    # produce a fake grad-cam
    heatmap = _random_heatmap(image_pil.size)
    gradcam_img = _apply_heatmap_to_image(image_pil, heatmap, alpha=0.45)

    return label, float(prob), gradcam_img
