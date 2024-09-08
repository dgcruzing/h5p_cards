"""
Functions to manage pdf content
"""

from io import BytesIO
from markdown import markdown
from weasyprint import HTML, CSS


def create_pdf_file(content):
    # Convert markdown to HTML
    html = markdown(content)
    
    # Create a BytesIO buffer for the PDF
    pdf_buffer = BytesIO()
    
    # Generate PDF from HTML
    HTML(string=html).write_pdf(
        pdf_buffer,
        stylesheets=[CSS(string='body { font-family: Arial, sans-serif; }')])
    
    # Move the buffer cursor to the beginning
    pdf_buffer.seek(0)
    
    return pdf_buffer
