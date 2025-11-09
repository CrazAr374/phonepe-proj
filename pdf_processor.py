"""
PDF Processing Module
Handles PDF extraction with password support
"""

import PyPDF2
import pdfplumber
import io
from typing import Optional


class PDFProcessor:
    """Extract text from PDF files"""
    
    def __init__(self, file_path: str, password: Optional[str] = None):
        self.file_path = file_path
        self.password = password
        
    def extract_text(self) -> str:
        """
        Extract text from PDF using multiple methods
        Returns concatenated text from all pages
        """
        # Try pdfplumber first (better for tables)
        try:
            text = self._extract_with_pdfplumber()
            if text and len(text.strip()) > 100:
                return text
        except Exception as e:
            print(f"pdfplumber failed: {e}")
        
        # Fallback to PyPDF2
        try:
            text = self._extract_with_pypdf2()
            if text and len(text.strip()) > 100:
                return text
        except Exception as e:
            print(f"PyPDF2 failed: {e}")
            
        raise ValueError("Could not extract text from PDF")
    
    def _extract_with_pdfplumber(self) -> str:
        """Extract using pdfplumber (better for structured data)"""
        text_parts = []
        
        with pdfplumber.open(self.file_path, password=self.password) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                
                # Try to extract tables separately
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if row:
                            text_parts.append(" | ".join([str(cell) if cell else "" for cell in row]))
        
        return "\n".join(text_parts)
    
    def _extract_with_pypdf2(self) -> str:
        """Extract using PyPDF2 (fallback method)"""
        text_parts = []
        
        with open(self.file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # Handle password-protected PDFs
            if reader.is_encrypted:
                if self.password:
                    reader.decrypt(self.password)
                else:
                    raise ValueError("PDF is encrypted but no password provided")
            
            # Extract text from all pages
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return "\n".join(text_parts)
    
    def get_metadata(self) -> dict:
        """Extract PDF metadata"""
        try:
            with open(self.file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                if reader.is_encrypted and self.password:
                    reader.decrypt(self.password)
                
                metadata = reader.metadata
                return {
                    'title': metadata.get('/Title', ''),
                    'author': metadata.get('/Author', ''),
                    'subject': metadata.get('/Subject', ''),
                    'creator': metadata.get('/Creator', ''),
                    'producer': metadata.get('/Producer', ''),
                    'num_pages': len(reader.pages)
                }
        except Exception as e:
            return {'error': str(e), 'num_pages': 0}


def extract_text_from_pdf(file_path: str, password: Optional[str] = None) -> str:
    """
    Convenience function to extract text from PDF
    
    Args:
        file_path: Path to PDF file
        password: Optional password for encrypted PDFs
        
    Returns:
        Extracted text as string
    """
    processor = PDFProcessor(file_path, password)
    return processor.extract_text()
