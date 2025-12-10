# app.py
import streamlit as st
from PIL import Image
import io
from utils.model import load_model, predict
import os

# Page configuration
st.set_page_config(page_title="Pneumonia Detector", page_icon="🏥", layout="centered")
st.title("🏥 Pneumonia Detector")
st.markdown(
    """
    Upload a chest X-ray image (PNG/JPG).  
    The app analyzes the image and predicts whether the lungs appear **Normal** or show signs of **Pneumonia**.  
    A heatmap overlay highlights the regions influencing the prediction.
    """
)

# Load model (mock for now)
@st.cache_resource
def get_model():
    return load_model()

model = get_model()

# Sidebar: sample picker
with st.sidebar:
    st.header("Choose a sample image")
    sample_files = os.listdir("samples")
    sample_files = [f for f in sample_files if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    sample_choice = st.selectbox("Select a sample", [""] + sample_files)

# Load image: either uploaded or from sample
uploaded = st.file_uploader("Upload chest X-ray image", type=["png", "jpg", "jpeg"])
if sample_choice:
    img_path = os.path.join("samples", sample_choice)
    img = Image.open(img_path).convert("RGB")
elif uploaded:
    img = Image.open(io.BytesIO(uploaded.read())).convert("RGB")
else:
    img = None

if img:
    st.image(img, caption="Selected image", width=700)

    if st.button("Run prediction"):
        with st.spinner("Running model..."):
            label, prob, gradcam = predict(img, model)
        st.success(f"Prediction: **{label}** ({prob*100:.1f}%)")
        st.image(gradcam, caption="Heatmap overlay highlighting key regions", width=700)
else:
    st.info("Upload a chest X-ray image or select a sample from the sidebar.")


# Sidebar instructions
with st.sidebar:
    st.header("Instructions")
    st.markdown("""
    1. Upload a chest X-ray image (PNG/JPG) or select a sample from the sidebar.  
    2. Click **Run prediction** to analyze the image.  
    3. View the prediction and the highlighted heatmap showing key regions.  
    4. Use this tool to quickly assess lung X-rays for signs of Pneumonia.
    """)
