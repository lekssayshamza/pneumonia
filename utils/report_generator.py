from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus import Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from PIL import Image as PILImage
import io
from datetime import datetime

def create_pdf_report(username, email, prediction_label, confidence, original_image, heatmap_image, output_path):
    """
    Create a professional PDF report for the patient
    
    Args:
        username: Patient/Doctor username
        email: Patient/Doctor email
        prediction_label: "Normal" or "Pneumonia"
        confidence: Confidence score (0-1)
        original_image: PIL Image of original X-ray
        heatmap_image: PIL Image of heatmap overlay
        output_path: Path to save the PDF
    """
    # Create PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                          rightMargin=0.75*inch, leftMargin=0.75*inch,
                          topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    # Title
    title = Paragraph("Chest X-Ray Analysis Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Patient Information Section
    elements.append(Paragraph("Patient Information", heading_style))
    
    # Create patient info table
    patient_data = [
        ['Doctor Name:', username],
        ['Email:', email],
        ['Report Date:', datetime.now().strftime("%B %d, %Y at %I:%M %p")]
    ]
    
    patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Analysis Results Section
    elements.append(Paragraph("Analysis Results", heading_style))
    
    # Determine result color and status
    if prediction_label == "Pneumonia":
        result_color = colors.HexColor('#dc3545')
        status_text = "Pneumonia Detected"
        recommendation = "The analysis indicates signs consistent with pneumonia. Please consult with a healthcare professional for proper diagnosis and treatment."
    else:
        result_color = colors.HexColor('#28a745')
        status_text = "Normal - No Pneumonia Detected"
        recommendation = "The analysis did not detect signs of pneumonia. However, this is not a substitute for professional medical evaluation."
    
    confidence_pct = confidence * 100
    
    # Results table
    results_data = [
        ['Diagnosis:', status_text],
        ['Confidence Level:', f'{confidence_pct:.1f}%'],
        ['Analysis Status:', 'High Confidence' if confidence > 0.8 else 'Medium Confidence' if confidence > 0.6 else 'Low Confidence']
    ]
    
    results_table = Table(results_data, colWidths=[2*inch, 4*inch])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('TEXTCOLOR', (1, 0), (1, 0), result_color),  # Diagnosis in color
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(results_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Recommendation
    rec_style = ParagraphStyle(
        'Recommendation',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#495057'),
        spaceAfter=12,
        alignment=TA_LEFT,
        fontName='Helvetica-Oblique',
        backColor=colors.HexColor('#fff3cd'),
        borderPadding=10
    )
    elements.append(Paragraph(f"<b>Recommendation:</b> {recommendation}", rec_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Images Section
    elements.append(Paragraph("X-Ray Images", heading_style))
    
    # Convert PIL images to bytes for reportlab
    def pil_to_bytes(img, max_width=3*inch):
        """Convert PIL Image to bytes and resize if needed"""
        img_copy = img.copy()
        # Resize if too large
        if img_copy.width > max_width:
            ratio = max_width / img_copy.width
            new_height = int(img_copy.height * ratio)
            img_copy = img_copy.resize((int(max_width), new_height), PILImage.Resampling.LANCZOS)
        
        img_bytes = io.BytesIO()
        img_copy.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes
    
    # Original image
    try:
        orig_img_bytes = pil_to_bytes(original_image, max_width=3*inch)
        orig_img = ReportLabImage(orig_img_bytes, width=3*inch, height=3*inch * (original_image.height / original_image.width))
        elements.append(Paragraph("<b>Original Chest X-Ray</b>", normal_style))
        elements.append(orig_img)
        elements.append(Spacer(1, 0.2*inch))
    except Exception as e:
        elements.append(Paragraph(f"<i>Original image could not be included: {str(e)}</i>", normal_style))
    
    # Heatmap image
    try:
        heatmap_img_bytes = pil_to_bytes(heatmap_image, max_width=3*inch)
        heatmap_img = ReportLabImage(heatmap_img_bytes, width=3*inch, height=3*inch * (heatmap_image.height / heatmap_image.width))
        elements.append(Paragraph("<b>Analysis Heatmap (Key Regions Highlighted)</b>", normal_style))
        elements.append(heatmap_img)
        elements.append(Spacer(1, 0.3*inch))
    except Exception as e:
        elements.append(Paragraph(f"<i>Heatmap image could not be included: {str(e)}</i>", normal_style))
    
    # Medical Disclaimer
    elements.append(Spacer(1, 0.2*inch))
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#6c757d'),
        spaceAfter=6,
        alignment=TA_LEFT,
        fontName='Helvetica-Oblique',
        backColor=colors.HexColor('#f8f9fa'),
        borderPadding=10
    )
    
    disclaimer_text = """
    <b>IMPORTANT MEDICAL DISCLAIMER:</b><br/>
    This report is generated using automated analysis tools and is provided for educational and research purposes only. 
    This application is NOT a substitute for professional medical diagnosis. Always consult qualified healthcare 
    professionals for medical decisions. Do not use this tool as the sole basis for treatment decisions. 
    Results may contain inaccuracies and should be reviewed and verified by medical experts.
    """
    elements.append(Paragraph(disclaimer_text, disclaimer_style))
    
    # Footer
    elements.append(Spacer(1, 0.3*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#6c757d'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph("Generated by Keep Awareness alive", footer_style))
    elements.append(Paragraph(f"Report ID: {datetime.now().strftime('%Y%m%d%H%M%S')}", footer_style))
    
    # Build PDF
    doc.build(elements)
    return output_path

