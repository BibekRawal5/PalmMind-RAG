from io import BytesIO
from typing import Tuple
from pdfminer.high_level import extract_text as pdf_extract_text

def extract_text(filename: str, content: bytes) -> Tuple[str, str]:
    try:
        if filename.lower().endswith('.txt'):
            return content.decode('utf-8', errors='ignore'), 'text/plain'
        if filename.lower().endswith('.pdf'):
            text = pdf_extract_text(BytesIO(content))
            return text, 'application/pdf'
    except Exception as e:
        raise ValueError('Unsupported file type')    
    raise ValueError('Unsupported file type')
