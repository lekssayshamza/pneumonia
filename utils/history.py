import streamlit as st
from utils.database import get_user_predictions, delete_prediction, get_prediction_count
from datetime import datetime

def show_history_page():
    """Display the history page with all past predictions"""
    st.markdown('<div class="main-header">Prediction History</div>', unsafe_allow_html=True)
    
    if 'user' not in st.session_state:
        st.error("You must be logged in to view history.")
        return
    
    user_id = st.session_state['user']['id']
    username = st.session_state['user']['username']
    
    # Get prediction count
    total_count = get_prediction_count(user_id)
    
    # Display stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Predictions", total_count)
    with col2:
        predictions = get_user_predictions(user_id)
        normal_count = sum(1 for p in predictions if p['label'] == 'Normal')
        st.metric("Normal Results", normal_count)
    with col3:
        pneumonia_count = sum(1 for p in predictions if p['label'] == 'Pneumonia')
        st.metric("Pneumonia Detected", pneumonia_count)
    
    st.markdown("---")
    
    # Get all predictions
    predictions = get_user_predictions(user_id)
    
    if not predictions:
        st.info("No prediction history yet. Upload and analyze an X-ray image to see your history here!")
        return
    
    # Display predictions
    st.markdown(f"### Your Recent Predictions ({len(predictions)} total)")
    
    # Filter options
    col1, col2 = st.columns([3, 1])
    with col1:
        filter_option = st.selectbox(
            "Filter by result",
            ["All", "Normal", "Pneumonia"],
            key="history_filter"
        )
    with col2:
        sort_option = st.selectbox(
            "Sort by",
            ["Most Recent", "Oldest First"],
            key="history_sort"
        )
    
    # Filter predictions
    filtered_predictions = predictions
    if filter_option != "All":
        filtered_predictions = [p for p in predictions if p['label'] == filter_option]
    
    # Sort predictions
    if sort_option == "Oldest First":
        filtered_predictions = list(reversed(filtered_predictions))
    
    st.markdown(f"Showing {len(filtered_predictions)} prediction(s)")
    st.markdown("---")
    
    # Display each prediction
    for idx, pred in enumerate(filtered_predictions):
        with st.container():
            # Create columns for layout
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.image(pred['image'], caption="X-ray Image", use_container_width=True)
            
            with col2:
                # Determine styling based on prediction
                if pred['label'] == "Normal":
                    box_class = "normal-box"
                    color = "#28a745"
                    icon = "✅"
                else:
                    box_class = "pneumonia-box"
                    color = "#dc3545"
                    icon = "⚠️"
                
                confidence_pct = pred['confidence'] * 100
                
                st.markdown(f"""
                <div class="prediction-box {box_class}" style="margin-bottom: 1rem;">
                    <h3 style="margin-bottom: 0.5rem;">
                        {icon} <strong>{pred['label']}</strong>
                    </h3>
                    <p style="font-size: 1.5rem; color: {color}; font-weight: bold; margin: 0.5rem 0;">
                        {confidence_pct:.1f}% Confidence
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Date and time
                try:
                    dt = datetime.strptime(pred['created_at'], "%Y-%m-%d %H:%M:%S")
                    formatted_date = dt.strftime("%B %d, %Y at %I:%M %p")
                except:
                    formatted_date = pred['created_at']
                
                st.markdown(f"**Date:** {formatted_date}")
                
                # Delete button
                if st.button("Delete", key=f"delete_{pred['id']}", use_container_width=True):
                    if delete_prediction(pred['id'], user_id):
                        st.success("Prediction deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete prediction.")
            
            with col3:
                st.markdown("### Details")
                st.metric("Result", pred['label'])
                st.metric("Confidence", f"{confidence_pct:.1f}%")
                st.metric("Status", "High" if pred['confidence'] > 0.8 else "Medium" if pred['confidence'] > 0.6 else "Low")
            
            st.markdown("---")

