# Car Lease AI - Contract Processing System

This project extracts and processes information from vehicle lease contract PDFs using Python, PDF text extraction, OCR, and AI-powered filtering.

## Features

- **PDF Text Extraction**: Extracts text from PDF lease contracts using `pdfplumber`
- **OCR Support**: Automatically detects scanned PDFs and uses Tesseract OCR for text extraction
- **Contract Filtering**: Extracts key lease information including:
  - Vehicle name (make, model, variant)
  - Monthly payment
  - Down payment / Initial rental
  - Lease term (months)
  - Annual mileage allowance
  - Excess mileage clause
  - Maintenance inclusion
  - Total lease cost
  - Vehicle specifications (fuel type, transmission, CO2 emissions, P11D value)
- **AI-Powered Extraction**: Uses Google Gemini AI as a fallback for vehicle name extraction when pattern matching fails
- **JSON Output**: Generates structured JSON files with extracted contract data

## Project Structure

```
car_lease_ai/
├── contracts/              # Input PDF files
├── extracted_text/         # Extracted text files (.txt)
├── filtered_output/       # Processed JSON files
├── extract_text.py        # PDF text extraction script
├── filter_contract.py    # Contract data extraction script
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Requirements

### Python Packages
- `pdfplumber` - PDF text extraction
- `pdf2image` - PDF to image conversion for OCR
- `pytesseract` - OCR text recognition
- `google-genai` - Google Gemini AI client

### System Dependencies
- **Tesseract OCR**: Required for scanned PDF processing
  - Windows: Download from [GitHub Tesseract releases](https://github.com/UB-Mannheim/tesseract/wiki)
  - Linux: `sudo apt-get install tesseract-ocr`
  - macOS: `brew install tesseract`

- **Poppler**: Required for `pdf2image`
  - Windows: Download from [Poppler for Windows](http://blog.alivate.com.au/poppler-windows/)
  - Linux: `sudo apt-get install poppler-utils`
  - macOS: `brew install poppler`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Sarvesh-Kannan/Springboard-Internship.git
cd Springboard-Internship
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/macOS: `source venv/bin/activate`

4. Install required packages:
```bash
pip install pdfplumber pdf2image pytesseract google-genai
```

5. Set up Tesseract OCR path (if needed):
   - The script will use the system PATH by default
   - For custom installation, set the path in `extract_text.py`:
     ```python
     pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
     ```

6. Set up Google Gemini API:
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Set the environment variable:
     ```bash
     export GOOGLE_API_KEY='your-api-key-here'
     ```
   - Or configure it in `filter_contract.py` directly

## Usage

### Step 1: Extract Text from PDFs

Place your PDF lease contracts in the `contracts/` folder, then run:

```bash
python extract_text.py
```

This will:
- Process all PDF files in the `contracts/` folder
- Extract text using `pdfplumber` (for text-based PDFs)
- Automatically use OCR for scanned PDFs
- Save extracted text to `extracted_text/` folder

### Step 2: Filter and Extract Contract Data

After text extraction, run:

```bash
python filter_contract.py
```

This will:
- Process all `.txt` files in `extracted_text/` folder
- Extract structured data from the text
- Generate JSON files in `filtered_output/` folder with extracted information

## Output Format

Each processed contract generates a JSON file with the following structure:

```json
{
    "vehicle_name": "BMW 3 Series 320d",
    "monthly_payment": "299.99",
    "down_payment": "1500.00",
    "lease_term_months": "36",
    "annual_mileage": "10000",
    "excess_mileage_clause": "Present",
    "maintenance_included": "No",
    "total_lease_cost": "12299.64",
    "fuel_type": "Diesel",
    "transmission": "Manual",
    "co2_emissions": "120 g/km",
    "p11d_value": "32000.00",
    "not_available_in_document": [
        "VIN number",
        "APR / Interest rate",
        "Residual value",
        "Purchase option / Buyout price",
        "Early termination penalties",
        "Late payment fees",
        "Warranty details",
        "Insurance coverage"
    ]
}
```

## Configuration

### Extracting Different Fields

To extract additional fields, modify the `extract_fields()` function in `filter_contract.py`:

```python
def extract_fields(text):
    # Add your custom regex patterns here
    # Example:
    # custom_match = re.search(r"your pattern", text_lower)
    # data["custom_field"] = custom_match.group(1) if custom_match else "Not Available"
```

### AI Fallback for Vehicle Name

The script uses Google Gemini AI as a fallback when pattern matching fails to extract the vehicle name. To use this feature:

1. Ensure your Google API key is configured
2. The `llm_extract_vehicle_name()` function will be called automatically if needed

## Troubleshooting

### OCR Not Working
- Ensure Tesseract OCR is installed and in your system PATH
- For Windows, verify the installation path matches your system

### PDF2Image Errors
- Install Poppler and ensure it's accessible
- Check that the PDF files are not corrupted

### Google Gemini API Errors
- Verify your API key is correct
- Check your internet connection
- Ensure you have API quota available

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is part of the Springboard Internship program.

## Author

Sarvesh Kannan

## Notes

- The `.gitignore` file is included to prevent committing virtual environments and other unnecessary files
- Always use a virtual environment for Python projects
- Keep your API keys secure and never commit them to the repository

