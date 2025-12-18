import streamlit as st
from PIL import Image
import io
import tempfile
from datetime import datetime
from utils.model import load_model, predict
from utils.auth import check_authentication, logout
from utils.history import show_history_page
from utils.database import save_prediction
from utils.report_generator import create_pdf_report
import os

# Page configuration
st.set_page_config(
    page_title="Pneumonia Detector", 
    page_icon="🏥", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .prediction-box {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .normal-box {
        background-color: #d4edda;
        border: 2px solid #28a745;
    }
    .pneumonia-box {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
    }
    .stProgress > div > div > div {
        background-color: #28a745;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Check authentication - show login/register if not authenticated
if not check_authentication():
    st.stop()  # Stop execution if not authenticated

# Load model
@st.cache_resource
def get_model():
    return load_model()

model = get_model()

# Sidebar (shared across tabs)
with st.sidebar:
    # User info and logout
    if 'user' in st.session_state:
        st.markdown(f"### 👤 Welcome, {st.session_state['user']['username']}!")
        st.markdown(f"📧 {st.session_state['user']['email']}")
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout()
        st.markdown("---")
    
    st.markdown("## Navigation")
    
    st.markdown("---")
    
    st.markdown("### Sample Images")
    sample_files = os.listdir("samples")
    sample_files = [f for f in sample_files if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    sample_choice = st.selectbox(
        "Select a sample image", 
        [""] + sample_files,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    st.markdown("### How to Use")
    with st.expander("Step-by-step guide"):
        st.markdown("""
        1. **Upload** a chest X-ray image (PNG/JPG) or **select** a sample from above
        2. Click **Analyze Image** to run the prediction
        3. Review the **prediction result** and **confidence score**
        4. Examine the **heatmap overlay** showing key regions
        5. Compare original and analyzed images side-by-side
        """)
    
    st.markdown("---")
    
    st.markdown("### About")
    st.info("""
    This application uses deep learning to analyze chest X-ray images and detect signs of pneumonia.
    
    The model highlights important regions using a heatmap visualization to help understand the prediction.
    """)

# Navigation tabs
tab1, tab2 = st.tabs(["🏥 Detection", "📊 History"])

# Detection Tab
with tab1:
    # Header
    st.markdown('<div class="main-header">Pneumonia Detection System</div>', unsafe_allow_html=True)
    
    # Subtitle and disclaimer
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <p style='font-size: 1.1rem; color: #666;'>
                Chest X-ray analysis for pneumonia detection
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Medical disclaimer
        with st.expander("Important Medical Disclaimer", expanded=False):
            st.warning("""
            **This tool is for educational and research purposes only.**
            
            - This application is NOT a substitute for professional medical diagnosis
            - Always consult qualified healthcare professionals for medical decisions
            - Do not use this tool as the sole basis for treatment decisions
            - Results may contain errors and should be verified by medical experts
            """)
    
    # Main content area
    st.markdown("---")
    
    # Image upload section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded = st.file_uploader(
            "Upload Chest X-ray Image", 
            type=["png", "jpg", "jpeg"],
            help="Upload a chest X-ray image in PNG, JPG, or JPEG format"
        )
    
    with col2:
        st.markdown("### Image Requirements")
        st.markdown("""
        - Format: PNG, JPG, or JPEG
        - Recommended: Clear, well-lit X-ray images
        - Best results: Frontal chest X-rays
        """)
    
    # Load image (sample_choice is from sidebar)
    if sample_choice:
        img_path = os.path.join("samples", sample_choice)
        img = Image.open(img_path).convert("RGB")
        st.info(f"Using sample image: **{sample_choice}**")
    elif uploaded:
        img = Image.open(io.BytesIO(uploaded.read())).convert("RGB")
        st.success("Image uploaded successfully!")
    else:
        img = None
    
    # Display results
    if img:
        st.markdown("---")
        
        # Display original image
        st.markdown("### Input Image")
        st.image(img, caption="Original Chest X-ray", use_container_width=True)
        
        # Prediction button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            predict_button = st.button(
                "Analyze Image", 
                type="primary",
                use_container_width=True,
                help="Click to analyze the image for pneumonia detection"
            )
        
        # Run prediction
        if predict_button:
            with st.spinner("Analyzing image... This may take a few seconds."):
                label, prob, gradcam = predict(img, model)
            
            # Store results in session state for PDF generation
            st.session_state['last_prediction'] = {
                'label': label,
                'confidence': prob,
                'image': img,
                'heatmap': gradcam
            }
            
            # Save prediction to database
            if 'user' in st.session_state:
                user_id = st.session_state['user']['id']
                success, result = save_prediction(user_id, label, prob, img)
                if success:
                    st.success("✅ Prediction saved to history!")
                else:
                    st.warning(f"⚠️ Could not save prediction: {result}")
            
            st.markdown("---")
            st.markdown("### Analysis Results")
            
            # Determine colors and styling based on prediction
            if label == "Normal":
                box_class = "normal-box"
                color = "#28a745"
                icon = "✅"
                prob_display = prob * 100
            else:
                box_class = "pneumonia-box"
                color = "#dc3545"
                icon = "⚠️"
                prob_display = prob * 100
            
            # Results display in columns
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown(f"""
                <div class="prediction-box {box_class}">
                    <h2 style="text-align: center; margin-bottom: 1rem;">
                        {icon} Prediction: <strong>{label}</strong>
                    </h2>
                    <div style="text-align: center; font-size: 2rem; color: {color}; font-weight: bold;">
                        {prob_display:.1f}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Confidence bar
                st.progress(prob, text=f"Confidence: {prob_display:.1f}%")
            
            with col2:
                # Metrics
                st.metric("Prediction", label)
                st.metric("Confidence Score", f"{prob_display:.1f}%")
                st.metric("Status", "Analysis Complete" if prob > 0.7 else "Review Recommended")
            
            st.markdown("---")
            
            # Side-by-side comparison
            st.markdown("### Visual Analysis")
            st.markdown("Compare the original image with the heatmap overlay highlighting key regions:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(img, caption="Original X-ray", use_container_width=True)
            
            with col2:
                st.image(gradcam, caption="Heatmap Overlay (Key Regions)", use_container_width=True)
            
            # Download Report Button
            st.markdown("---")
            st.markdown("### Download Report")
            st.markdown("Generate a PDF report for the patient with all analysis details.")
            
            if 'last_prediction' in st.session_state and 'user' in st.session_state:
                pred = st.session_state['last_prediction']
                username = st.session_state['user']['username']
                email = st.session_state['user']['email']
                
                # Create temporary file for PDF
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    pdf_path = tmp_file.name
                
                try:
                    # Generate PDF
                    create_pdf_report(
                        username=username,
                        email=email,
                        prediction_label=pred['label'],
                        confidence=pred['confidence'],
                        original_image=pred['image'],
                        heatmap_image=pred['heatmap'],
                        output_path=pdf_path
                    )
                    
                    # Read PDF file
                    with open(pdf_path, 'rb') as pdf_file:
                        pdf_bytes = pdf_file.read()
                    
                    # Download button
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"Pneumonia_Report_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True,
                        help="Download a comprehensive PDF report with all analysis details"
                    )
                    
                    # Clean up
                    os.unlink(pdf_path)
                    
                except Exception as e:
                    st.error(f"Error generating PDF report: {str(e)}")
                    if os.path.exists(pdf_path):
                        os.unlink(pdf_path)
            
            st.markdown("---")
            
            # Additional information
            with st.expander("Detailed Analysis Information"):
                st.markdown(f"""
                **Prediction Details:**
                - **Result:** {label}
                - **Confidence:** {prob_display:.2f}%
                - **Interpretation:** {'The model detected signs consistent with pneumonia. Please consult a healthcare professional for proper diagnosis.' if label == 'Pneumonia' else 'The model did not detect signs of pneumonia. However, this is not a substitute for professional medical evaluation.'}
                
                **About the Heatmap:**
                - Red/orange regions indicate areas that most influenced the prediction
                - Darker regions are more significant in the model's decision
                - This visualization helps understand what the AI is focusing on
                """)
                
                if prob < 0.6:
                    st.warning("Low confidence prediction. The result may be less reliable. Please consult a medical professional.")
                elif prob > 0.9:
                    st.success("High confidence prediction. However, always verify with medical professionals.")
    else:
        st.markdown("---")
        st.info("Please upload a chest X-ray image or select a sample image from the sidebar to begin analysis.")

# History Tab
with tab2:
    show_history_page()
