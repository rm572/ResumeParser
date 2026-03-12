"""PDF extraction utilities for resume processing."""

import io
from typing import Optional
import PyPDF2


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF bytes.
    
    Args:
        pdf_bytes: PDF file content as bytes
        
    Returns:
        Extracted text from all pages
        
    Raises:
        ValueError: If PDF is invalid or cannot be read
    """
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        if len(pdf_reader.pages) == 0:
            raise ValueError("PDF has no pages")
        
        text_content = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                text_content += text + "\n"
        
        if not text_content.strip():
            raise ValueError("No text content found in PDF")
        
        return text_content.strip()
    
    except PyPDF2.PdfReadError as e:
        raise ValueError(f"Failed to read PDF: {str(e)}")
    except Exception as e:
        raise ValueError(f"PDF extraction error: {str(e)}")


def validate_pdf(pdf_bytes: bytes) -> bool:
    """
    Validate if bytes represent a valid PDF.
    
    Args:
        pdf_bytes: File content as bytes
        
    Returns:
        True if valid PDF, False otherwise
    """
    try:
        if not pdf_bytes.startswith(b"%PDF"):
            return False
        
        pdf_file = io.BytesIO(pdf_bytes)
        PyPDF2.PdfReader(pdf_file)
        return True
    except Exception:
        return False
