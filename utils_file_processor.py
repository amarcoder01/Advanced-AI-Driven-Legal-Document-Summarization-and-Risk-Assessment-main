import os
import logging
from docx import Document
from pdf_processor import extract_text_from_pdf
import streamlit as st
import PyPDF2
import io

def extract_text_from_uploaded_file(uploaded_file):
    """
    Extract text from an uploaded file.
    Currently supports PDF and TXT files.
    
    Args:
        uploaded_file: The uploaded file object from Streamlit
        
    Returns:
        str: Extracted text from the file
    """
    try:
        # Get file type
        file_type = uploaded_file.type
        
        # Process based on file type
        if file_type == "application/pdf":
            return extract_text_from_pdf(uploaded_file)
        elif file_type == "text/plain":
            return extract_text_from_txt(uploaded_file)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
            
    except Exception as e:
        logging.error(f"Error extracting text from file: {str(e)}")
        raise

def extract_text_from_pdf(pdf_file):
    """
    Extract text from a PDF file.
    
    Args:
        pdf_file: The uploaded PDF file object
        
    Returns:
        str: Extracted text from the PDF
    """
    try:
        # Create PDF reader object
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
        
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {str(e)}")
        raise

def extract_text_from_txt(txt_file):
    """
    Extract text from a TXT file.
    
    Args:
        txt_file: The uploaded TXT file object
        
    Returns:
        str: Extracted text from the TXT file
    """
    try:
        # Read text file content
        text = txt_file.read().decode("utf-8")
        return text.strip()
        
    except Exception as e:
        logging.error(f"Error extracting text from TXT file: {str(e)}")
        raise

def extract_docx_text(uploaded_file):
    """Extract text from DOCX files."""
    try:
        document = Document(uploaded_file)
        full_text = [para.text for para in document.paragraphs]
        return "\n".join(full_text)
    except Exception as e:
        logging.error(f"Error reading DOC/DOCX: {str(e)}")
        return None

def extract_txt_text(uploaded_file):
    """Extract text from TXT files."""
    try:
        return uploaded_file.getvalue().decode("utf-8")
    except Exception as e:
        logging.error(f"Error reading TXT: {str(e)}")
        return None 