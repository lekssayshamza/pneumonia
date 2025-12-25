import streamlit as st
from PIL import Image
import io
import tempfile
from datetime import datetime
from utils.new_model import load_model, predict
from utils.auth import check_authentication, logout
from utils.history import show_history_page
from utils.database import save_prediction
from utils.report_generator import (
    create_pdf_report, 
    create_excel_report, 
    create_word_report, 
    create_csv_report, 
    create_json_report, 
    create_html_report
)
from utils.chat_utils import get_ai_response
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
        st.markdown(f"### Welcome, {st.session_state['user']['username']}!")
        st.markdown(f"{st.session_state['user']['email']}")
        st.markdown("---")
        if st.button("Logout", use_container_width=True, type="secondary"):
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
tab1, tab2 = st.tabs(["Detection", "History"])

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
                    st.success("Prediction saved to history!")
                else:
                    st.warning(f"Could not save prediction: {result}")
        
        # Display results if prediction exists (either from current or previous analysis)
        if 'last_prediction' in st.session_state:
            pred = st.session_state['last_prediction']
            label = pred['label']
            prob = pred['confidence']
            gradcam = pred['heatmap']
            
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
                st.image(pred['image'], caption="Original X-ray", use_container_width=True)
            
            with col2:
                st.image(gradcam, caption="Heatmap Overlay (Key Regions)", use_container_width=True)
            
            # Download Report Section
            st.markdown("---")
            st.markdown("### Download Report")
            st.markdown("Generate reports in multiple formats for the patient with all analysis details.")
            
            if 'user' in st.session_state:
                pred = st.session_state['last_prediction']
                username = st.session_state['user']['username']
                email = st.session_state['user']['email']
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                # Create columns for download buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    # PDF Report
                    pdf_path = None
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                            pdf_path = tmp_file.name
                        
                        create_pdf_report(
                            username=username,
                            email=email,
                            prediction_label=pred['label'],
                            confidence=pred['confidence'],
                            original_image=pred['image'],
                            heatmap_image=pred['heatmap'],
                            output_path=pdf_path
                        )
                        
                        with open(pdf_path, 'rb') as pdf_file:
                            pdf_bytes = pdf_file.read()
                        
                        st.download_button(
                            label="📄 Download PDF Report",
                            data=pdf_bytes,
                            file_name=f"Pneumonia_Report_{username}_{timestamp}.pdf",
                            mime="application/pdf",
                            type="primary",
                            use_container_width=True,
                            help="Download a comprehensive PDF report"
                        )
                        
                        os.unlink(pdf_path)
                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")
                        if pdf_path and os.path.exists(pdf_path):
                            os.unlink(pdf_path)
                    
                    # Excel Report
                    excel_path = None
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                            excel_path = tmp_file.name
                        
                        create_excel_report(
                            username=username,
                            email=email,
                            prediction_label=pred['label'],
                            confidence=pred['confidence'],
                            original_image=pred['image'],
                            heatmap_image=pred['heatmap'],
                            output_path=excel_path
                        )
                        
                        with open(excel_path, 'rb') as excel_file:
                            excel_bytes = excel_file.read()
                        
                        st.download_button(
                            label="📊 Download Excel Report",
                            data=excel_bytes,
                            file_name=f"Pneumonia_Report_{username}_{timestamp}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                            help="Download report in Excel format"
                        )
                        
                        os.unlink(excel_path)
                    except Exception as e:
                        st.error(f"Error generating Excel: {str(e)}")
                        if excel_path and os.path.exists(excel_path):
                            os.unlink(excel_path)
                    
                    # Word Report
                    word_path = None
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                            word_path = tmp_file.name
                        
                        create_word_report(
                            username=username,
                            email=email,
                            prediction_label=pred['label'],
                            confidence=pred['confidence'],
                            original_image=pred['image'],
                            heatmap_image=pred['heatmap'],
                            output_path=word_path
                        )
                        
                        with open(word_path, 'rb') as word_file:
                            word_bytes = word_file.read()
                        
                        st.download_button(
                            label="📝 Download Word Report",
                            data=word_bytes,
                            file_name=f"Pneumonia_Report_{username}_{timestamp}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True,
                            help="Download report in Word format"
                        )
                        
                        os.unlink(word_path)
                    except Exception as e:
                        st.error(f"Error generating Word: {str(e)}")
                        if word_path and os.path.exists(word_path):
                            os.unlink(word_path)
                
                with col2:
                    # CSV Report
                    csv_path = None
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                            csv_path = tmp_file.name
                        
                        create_csv_report(
                            username=username,
                            email=email,
                            prediction_label=pred['label'],
                            confidence=pred['confidence'],
                            original_image=pred['image'],
                            heatmap_image=pred['heatmap'],
                            output_path=csv_path
                        )
                        
                        with open(csv_path, 'rb') as csv_file:
                            csv_bytes = csv_file.read()
                        
                        st.download_button(
                            label="📋 Download CSV Report",
                            data=csv_bytes,
                            file_name=f"Pneumonia_Report_{username}_{timestamp}.csv",
                            mime="text/csv",
                            use_container_width=True,
                            help="Download report in CSV format"
                        )
                        
                        os.unlink(csv_path)
                    except Exception as e:
                        st.error(f"Error generating CSV: {str(e)}")
                        if csv_path and os.path.exists(csv_path):
                            os.unlink(csv_path)
                    
                    # JSON Report
                    json_path = None
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp_file:
                            json_path = tmp_file.name
                        
                        create_json_report(
                            username=username,
                            email=email,
                            prediction_label=pred['label'],
                            confidence=pred['confidence'],
                            original_image=pred['image'],
                            heatmap_image=pred['heatmap'],
                            output_path=json_path
                        )
                        
                        with open(json_path, 'rb') as json_file:
                            json_bytes = json_file.read()
                        
                        st.download_button(
                            label="📦 Download JSON Report",
                            data=json_bytes,
                            file_name=f"Pneumonia_Report_{username}_{timestamp}.json",
                            mime="application/json",
                            use_container_width=True,
                            help="Download report in JSON format"
                        )
                        
                        os.unlink(json_path)
                    except Exception as e:
                        st.error(f"Error generating JSON: {str(e)}")
                        if json_path and os.path.exists(json_path):
                            os.unlink(json_path)
                    
                    # HTML Report
                    html_path = None
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp_file:
                            html_path = tmp_file.name
                        
                        create_html_report(
                            username=username,
                            email=email,
                            prediction_label=pred['label'],
                            confidence=pred['confidence'],
                            original_image=pred['image'],
                            heatmap_image=pred['heatmap'],
                            output_path=html_path
                        )
                        
                        with open(html_path, 'rb') as html_file:
                            html_bytes = html_file.read()
                        
                        st.download_button(
                            label="🌐 Download HTML Report",
                            data=html_bytes,
                            file_name=f"Pneumonia_Report_{username}_{timestamp}.html",
                            mime="text/html",
                            use_container_width=True,
                            help="Download report in HTML format"
                        )
                        
                        os.unlink(html_path)
                    except Exception as e:
                        st.error(f"Error generating HTML: {str(e)}")
                        if html_path and os.path.exists(html_path):
                            os.unlink(html_path)
                
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

# --------------------------------------------------------------------------
# Floating Chat Interface (Bottom Right)
# --------------------------------------------------------------------------

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Create the chat interface (Floating)
# We don't use columns here because we position it absolutely/fixed with CSS

# Use popover for the chat interface
# The button text is an emoji to make it small and icon-like
with st.popover("🤖", help="Chat with AI Assistant"):
    col_header, col_clear = st.columns([3, 1])
    with col_header:
        st.markdown("### 🩺 Medical Assistant")
    with col_clear:
        if st.button("🗑️", help="Clear Chat History", key="clear_chat_btn"):
            st.session_state.messages = []
            st.rerun()
    
    # Container for chat messages
    chat_container = st.container(height=400)
    
    with chat_container:
        # Display chat messages from history
        if not st.session_state.messages:
             st.info("Hello! I'm your AI medical assistant. How can I help you today?")
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Ask about pneumonia...", key="chat_input"):
        # Display user message
        with chat_container:
            st.chat_message("user").markdown(prompt)
        
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display assistant response
        with chat_container:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("Thinking...")
                
                full_response = get_ai_response(st.session_state.messages)
                message_placeholder.markdown(full_response)
        
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        # Rerun to update
        st.rerun()

# Custom CSS to style the popover button to look more like a floating circle button
st.markdown("""
<style>
    /* Position the popover container fixed at the bottom right */
    /* We use !important to ensure it overrides default Streamlit styling */
    div[data-testid="stPopover"] {
        position: fixed !important;
        bottom: 30px !important;
        right: 30px !important;
        width: auto !important;
        z-index: 99999 !important;
    }

    /* Style the button inside the popover container */
    div[data-testid="stPopover"] > button {
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        padding: 0 !important;
        font-size: 24px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        border: none !important;
        background-color: #4FC3F7 !important;
        color: white !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    div[data-testid="stPopover"] > button:hover {
        transform: scale(1.1) !important;
        background-color: #039BE5 !important;
        color: white !important;
        box-shadow: 0 6px 14px rgba(0,0,0,0.4) !important;
    }

    /* Hide the default dropdown arrow/chevron */
    div[data-testid="stPopover"] > button span[class*="e16nr0p33"] {
        display: none !important;
    }
    div[data-testid="stPopover"] > button svg {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)
