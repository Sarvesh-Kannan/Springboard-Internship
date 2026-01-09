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

INPUT_FOLDER = "extracted_text"
OUTPUT_FOLDER = "fineline_output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ------------------------
# SAFE JSON PARSER
# ------------------------
def safe_json_parse(llm_output: str) -> dict:
    """
    Try to parse JSON from LLM output.
    If invalid, extract the first {...} block using regex.
    """
    try:
        return json.loads(llm_output)
    except json.JSONDecodeError:
        # Extract first JSON object from text
        match = re.search(r"\{.*\}", llm_output, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                return {}
        return {}

# ------------------------
# LLM EXTRACTION
# ------------------------
def llm_extract_contract(text):
    prompt = f"""
You are an expert in analyzing vehicle lease contracts.

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
{text[:3000]}
"""
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",  # Change to a working model if needed
            contents=prompt
        )
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
# PROCESS FILES
# ------------------------
for file in os.listdir(INPUT_FOLDER):
    if not file.endswith(".txt"):
        continue

    print(f"Processing: {file}")

    with open(os.path.join(INPUT_FOLDER, file), "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Remove obvious noise: long numbers, emails
    cleaned_text = re.sub(r"\b\d{5,}\b", "", raw_text)
    cleaned_text = re.sub(r"\S+@\S+", "", cleaned_text)

    data = llm_extract_contract(cleaned_text)

    # Fallback vehicle name if missing
    if not data or data.get("car_name", "").strip().lower() in ["", "information not available"]:
        data["car_name"] = extract_vehicle_name(raw_text)

    output_path = os.path.join(
        OUTPUT_FOLDER, file.replace(".txt", ".json")
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

print("\n✅ All contracts processed successfully!")
