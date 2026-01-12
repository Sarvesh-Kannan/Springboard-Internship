import os
import re
import json
import re
from google import genai

# ------------------------
# CONFIG
# ------------------------
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Please set the GOOGLE_API_KEY environment variable before running.")

client = genai.Client(api_key=api_key)


# ------------------------
# SAFE JSON PARSER
# ------------------------
def safe_json_parse(llm_output: str) -> dict:
    import json, re

    match = re.search(r"\{[\s\S]*\}", llm_output)
    if not match:
        raise ValueError("No JSON object found in LLM output")

    json_text = match.group()

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from LLM: {e}")


CANONICAL_SCHEMA = {
    "1. Vehicle Consultancy / Dealer Info": {
        "Vehicle Consultancy Name": "Information not available",
        "Contact Details": "Information not available",
        "Dealer / Lessor Name": "Information not available",
        "Location": "Information not available"
    },
    "2. Vehicle Identification & Basic Details": {
        "Car Name / Model": "Information not available",
        "Variant": "Information not available",
        "Vehicle Identification Number (VIN)": "Information not available",
        "Registered Number": "Information not available",
        "VAT Number": "Information not available",
        "Manufacturer": "Information not available",
        "Manufacturer OTR": "Information not available",
        "P11D (Official List Price)": "Information not available"
    },
    "3. Vehicle Specifications": {
        "Body Type": "Information not available",
        "Car Color": "Information not available",
        "Fuel Type (Petrol / Diesel / Electric / Hybrid)": "Information not available",
        "Transmission (Manual / Automatic)": "Information not available",
        "CO₂ Emissions": "Information not available",
        "Vehicle Depreciation Rate per Month": "Information not available",
        "Mileage and Tenure Limit": "Information not available"
    },
    "4. Lease Terms / Agreement Details": {
        "Agreement Duration / Term Period": "Information not available",
        "Rental Period (Start / End Dates)": "Information not available",
        "Expiry Date": "Information not available",
        "Termination Date": "Information not available",
        "Early Termination Fee": "Information not available",
        "Mileage Allowance": "Information not available",
        "Maintenance Responsibility": "Information not available",
        "Insurance Management Requirements": "Information not available",
        "Other Terms and Conditions / Disclaimer": "Information not available"
    },
    "5. Payment Details": {
        "5.1 Upfront / Signing Payments": {
            "Lease Signing Payment / Amount Due at Lease Signing or Delivery": "Information not available",
            "Capitalized Cost Reduction": "Information not available",
            "Net Trade-In Allowance": "Information not available",
            "Down Payment": "Information not available",
            "First Monthly Payment": "Information not available",
            "Refundable Security eposit": "Information not available",
            "Amount to be Paid in Cash": "Information not available",
            "Title Fees": "Information not available",
            "Registration Fees": "Information not available",
            "Processing Fee": "Information not available"
        },
        "5.2 Recurring Payments": {
            "Monthly Payments / Fixed Monthly Rent": "Information not available",
            "Monthly Sales / Use Tax": "Information not available",
            "Other Charges (not part of monthly payment)": "Information not available",
            "Total Monthly Payment (per annum or per month)": "Information not available",
            "Total of Payments (over entire lease)": "Information not available",
            "Amortized Amount over the Period of Lease": "Information not available"
        }
    },
    "6. Taxes & Additional Fees": {
        "VAT / Sales Tax": "Information not available",
        "Other Fees and Taxes": "Information not available"
    },
    "7. Residual & End-of-Lease Details": {
        "Residual Value": "Information not available",
        "Vehicle Depreciation Considered": "Information not available",
        "Options at Lease End (return / buy / renew)": "Information not available"
    }
}
# -------------------------
#Normalizer
#------------------------

def normalize_llm_output(llm_data: dict, raw_text: str) -> dict:
    """
    Forces LLM output into the canonical 7-section schema.
    Never fails.
    """

    result = json.loads(json.dumps(CANONICAL_SCHEMA))  # deep copy

    if not isinstance(llm_data, dict):
        return result

    for section, fields in result.items():
        if section not in llm_data or not isinstance(llm_data.get(section), dict):
            continue

        for key in fields:
            value = llm_data[section].get(key)
            if isinstance(value, str) and value.strip():
                result[section][key] = value

    # 🚑 Fallback car name if missing
    if result["2. Vehicle Identification & Basic Details"]["Car Name / Model"] == "Information not available":
        result["2. Vehicle Identification & Basic Details"]["Car Name / Model"] = extract_vehicle_name(raw_text)

    return result



# ------------------------
# LLM EXTRACTION
# ------------------------
def llm_extract_contract(response_text):
    prompt = f"""
You are an expert in analyzing vehicle lease contracts and a data extraction system.

Return ONLY valid JSON.
No explanations.
No markdown.
No extra text.

Use EXACTLY this JSON structure:
Extract the following fields.
If missing, return "Information not available".

Return ONLY valid JSON.

Fields:
1. Vehicle Consultancy / Dealer Info
Vehicle Consultancy Name
Contact Details
Dealer / Lessor Name
Location

2. Vehicle Identification & Basic Details
Car Name / Model
Variant
Vehicle Identification Number (VIN)
Registered Number
VAT Number
Manufacturer
Manufacturer OTR
P11D (Official List Price)

3. Vehicle Specifications
Body Type
Car Color
Fuel Type (Petrol / Diesel / Electric / Hybrid)
Transmission (Manual / Automatic)
CO₂ Emissions
Vehicle Depreciation Rate per Month
Mileage and Tenure Limit

4. Lease Terms / Agreement Details
Agreement Duration / Term Period
Rental Period (Start / End Dates)
Expiry Date
Termination Date
Early Termination Fee
Mileage Allowance
Maintenance Responsibility
Insurance Management Requirements
Other Terms and Conditions / Disclaimer

5. Payment Details
5.1 Upfront / Signing Payments
Lease Signing Payment / Amount Due at Lease Signing or Delivery
Capitalized Cost Reduction
Net Trade-In Allowance
Down Payment
First Monthly Payment
Refundable Security eposit
Amount to be Paid in Cash
Title Fees
Registration Fees
Processing Fee

5.2 Recurring Payments
Monthly Payments / Fixed Monthly Rent
Monthly Sales / Use Tax
Other Charges (not part of monthly payment)
Total Monthly Payment (per annum or per month)
Total of Payments (over entire lease)
Amortized Amount over the Period of Lease

6. Taxes & Additional Fees
VAT / Sales Tax
Other Fees and Taxes

7. Residual & End-of-Lease Details
Residual Value
Vehicle Depreciation Considered
Options at Lease End (return / buy / renew)

TEXT:
{response_text[:8000]}
"""
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",  # Change to a working model if needed
            contents=prompt
        )
        print("RAW LLM OUTPUT:\n", response.text) 
        return safe_json_parse(response.text)
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return {}

# ------------------------
# VEHICLE NAME (HEURISTIC)
# ------------------------
def extract_vehicle_name(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for i, line in enumerate(lines):
        # Skip numeric-heavy lines or emails
        if sum(c.isdigit() for c in line) > len(line) * 0.4:
            continue
        if "@" in line:
            continue
        if any(k in line.lower() for k in ["vat", "consultancy", "tel", "email", "registered"]):
            continue
        if re.search(r"[A-Za-z]", line):
            # Combine with next line if it looks like a variant
            if i + 1 < len(lines) and re.search(r"[A-Za-z]", lines[i + 1]):
                return f"{line} {lines[i + 1]}"
            return line
    return "Information not available"

# ------------------------
# PROCESS FILES USING FUNCTION
# ------------------------

def process_text(raw_text: str) -> dict:
    # Clean noise
    cleaned_text = re.sub(r"\b\d{5,}\b", "", raw_text)
    cleaned_text = re.sub(r"\S+@\S+", "", cleaned_text)

    # Call LLM
    try:
        llm_data = llm_extract_contract(cleaned_text)
    except Exception as e:
        return normalize_llm_output({}, raw_text)

    # Normalize ALWAYS
    return normalize_llm_output(llm_data, raw_text)

