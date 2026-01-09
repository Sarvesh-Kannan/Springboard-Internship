import os
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import pdfplumber

# Folder containing PDFs and images
INPUT_FOLDER = "contract_format_inputs"
OUTPUT_FILE = "contract_format_detailed.txt"  # single file to save all text

# Supported file extensions
IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]
PDF_EXTENSIONS = [".pdf"]

def ocr_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def ocr_pdf(pdf_path):
    text = ""
    try:
        # Try pdfplumber first for text-based PDFs
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        # If no text found, fallback to OCR on images
        if not text.strip():
            pages = convert_from_path(pdf_path, dpi=300)
            for page in pages:
                text += pytesseract.image_to_string(page) + "\n"
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
    return text

def process_folder(folder_path, output_file):
    all_text = ""
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        name, ext = os.path.splitext(filename)
        ext = ext.lower()
        
        text = ""
        if ext in IMAGE_EXTENSIONS:
            text = ocr_image(file_path)
        elif ext in PDF_EXTENSIONS:
            text = ocr_pdf(file_path)
        else:
            print(f"Skipping unsupported file: {filename}")
            continue
        
        # Optional: add file separator
        all_text += f"\n\n--- Start of {filename} ---\n\n"
        all_text += text
        all_text += f"\n--- End of {filename} ---\n\n"
        print(f"Processed {filename}")
    
    # Save all text to a single file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(all_text)
    print(f"All extracted text saved to {output_file}")

# Run the extraction
process_folder(INPUT_FOLDER, OUTPUT_FILE)
