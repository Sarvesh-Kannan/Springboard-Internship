import os
import pdfplumber
from pdf2image import convert_from_path
import pytesseract

PDF_FOLDER = "contracts"
OUTPUT_FOLDER = "extracted_text"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for pdf_file in os.listdir(PDF_FOLDER):
    if not pdf_file.endswith(".pdf"):
        continue

    pdf_path = os.path.join(PDF_FOLDER, pdf_file)
    output_text = ""

    print(f"\nProcessing: {pdf_file}")

    # extracting text 
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                output_text += page_text + "\n"

    # Using OCR
    if output_text.strip() == "":
        print("Scanned PDF detected. Running OCR...")
        images = convert_from_path(pdf_path)

        for img in images:
            ocr_text = pytesseract.image_to_string(img)
            output_text += ocr_text + "\n"
    else:
        print("Text-based PDF detected.")

    # Save extracted text
    txt_filename = pdf_file.replace(".pdf", ".txt")
    txt_path = os.path.join(OUTPUT_FOLDER, txt_filename)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(output_text)

    print(f"Saved: {txt_filename}")

print("\n All PDFs processed successfully!")
