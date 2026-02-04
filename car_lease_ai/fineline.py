import os
import re
import json
from google import genai

# ========================
# CONFIG
# ========================
API_KEY = os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY environment variable not set")

client = genai.Client(api_key=API_KEY)

# ========================
# SAFE JSON PARSER
# ========================
def safe_json_parse(text: str) -> dict:
    """
    Ensures we always return a dictionary even if LLM output is messy.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                return {}
        return {}

# ========================
# LLM EXTRACTION
# ========================
def llm_extract_contract(contract_text: str) -> dict:
    """
    Uses Gemini LLM to extract structured lease information.
    """

    prompt = f"""
You are an expert system for extracting structured information from vehicle lease contracts.

INSTRUCTIONS:
- Extract ALL fields listed below.
- If a field is missing, return "Information not available".
- Return ONLY valid JSON.
- Preserve section structure exactly.

OUTPUT JSON STRUCTURE:

{{
  "1. Vehicle Consultancy / Dealer Info": {{
    "Vehicle Consultancy Name": "",
    "Contact Details": "",
    "Dealer / Lessor Name": "",
    "Location": ""
  }},
  "2. Vehicle Identification & Basic Details": {{
    "Car Name / Model": "",
    "Variant": "",
    "Vehicle Identification Number (VIN)": "",
    "Registered Number": "",
    "VAT Number": "",
    "Manufacturer": "",
    "Manufacturer OTR": "",
    "P11D (Official List Price)": ""
  }},
  "3. Vehicle Specifications": {{
    "Body Type": "",
    "Car Color": "",
    "Fuel Type": "",
    "Transmission": "",
    "CO₂ Emissions": "",
    "Vehicle Depreciation Rate per Month": "",
    "Mileage and Tenure Limit": ""
  }},
  "4. Lease Terms / Agreement Details": {{
    "Agreement Duration / Term Period": "",
    "Rental Period (Start / End Dates)": "",
    "Expiry Date": "",
    "Termination Date": "",
    "Early Termination Fee": "",
    "Mileage Allowance": "",
    "Maintenance Responsibility": "",
    "Insurance Management Requirements": "",
    "Other Terms and Conditions / Disclaimer": ""
  }},
  "5. Payment Details": {{
    "5.1 Upfront / Signing Payments": {{
      "Lease Signing Payment": "",
      "Capitalized Cost Reduction": "",
      "Net Trade-In Allowance": "",
      "Down Payment": "",
      "First Monthly Payment": "",
      "Refundable Security Deposit": "",
      "Amount to be Paid in Cash": "",
      "Title Fees": "",
      "Registration Fees": "",
      "Processing Fee": ""
    }},
    "5.2 Recurring Payments": {{
      "Monthly Payments": "",
      "Monthly Sales / Use Tax": "",
      "Other Charges": "",
      "Total Monthly Payment": "",
      "Total of Payments": "",
      "Amortized Amount over Lease": ""
    }}
  }},
  "6. Taxes & Additional Fees": {{
    "VAT / Sales Tax": "",
    "Other Fees and Taxes": ""
  }},
  "7. Residual & End-of-Lease Details": {{
    "Residual Value": "",
    "Vehicle Depreciation Considered": "",
    "Options at Lease End": ""
  }}
}}

CONTRACT TEXT:
\"\"\"
{contract_text[:3500]}
\"\"\"
"""

    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt
        )
        return safe_json_parse(response.text)

    except Exception as e:
        print("LLM ERROR:", e)
        return {}

# ========================
# PUBLIC FUNCTION (USED BY FASTAPI)
# ========================
def process_text(raw_text: str) -> dict:
    """
    Entry point used by FastAPI.
    Takes raw extracted text and returns structured JSON.
    """

    if not raw_text or not raw_text.strip():
        return {"error": "Empty contract text"}

    # Basic noise cleanup (safe)
    cleaned_text = re.sub(r"\S+@\S+", "", raw_text)
    cleaned_text = re.sub(r"\b\d{8,}\b", "", cleaned_text)

    extracted_data = llm_extract_contract(cleaned_text)

    return extracted_data
