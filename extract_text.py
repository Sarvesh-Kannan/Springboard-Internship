import pdfplumber
from pdf2image import convert_from_path
import pytesseract

def extract_text(pdf_path: str) -> str:
    output_text = ""

    # Try normal text extraction
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                output_text += text + "\n"

    # If no text found → OCR
    if not output_text.strip():
        images = convert_from_path(pdf_path)
        for img in images:
            output_text += pytesseract.image_to_string(img) + "\n"

    return output_text
