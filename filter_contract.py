import os
import re
import json
from google import genai

INPUT_FOLDER = "extracted_text"
OUTPUT_FOLDER = "filtered_output"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ------------------------
# LLM CLIENT (FALLBACK ONLY)
# ------------------------
client = genai.Client()

def llm_extract_vehicle_name(text):
    prompt = f"""
You are given raw text from a vehicle lease document.

Extract ONLY the vehicle name (make + model + variant if present).
Do NOT include prices, phone numbers, company names, or extra words.

If you cannot confidently find it, reply exactly:
Not Available

Text:
{text[:1500]}
"""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )

    return response.text.strip()

# ------------------------
# VEHICLE NAME EXTRACTION
# ------------------------
def extract_vehicle_name(text):
    """
    Extract the vehicle name from the first line that looks like a vehicle title.
    Ignores phone numbers, emails, VAT, consultancy names, and numeric-only lines.
    Combines next line if it seems like a variant/trim.
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    for i in range(len(lines)):
        line = lines[i]

        # Skipping lines with numbers or emails
        if sum(c.isdigit() for c in line) > len(line) * 0.4:
            continue
        if "@" in line:
            continue

        # Skipping noise
        if any(
            keyword in line.lower()
            for keyword in [
                "vat", "contract", "consultancy", "tel", "phone",
                "email", "advert", "fee", "office", "company", "registered"
            ]
        ):
            continue

        # Must contain letters (vehicle name)
        if re.search(r"[A-Za-z]", line):
            # Combine with next line if it looks like a trim/variant
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if re.search(r"[A-Za-z]", next_line) and sum(c.isdigit() for c in next_line) < len(next_line) * 0.4:
                    return f"{line} {next_line}"
            return line

    return "Not Available"


# ------------------------
# FIELD EXTRACTION WITH NOISE FILTERING
# ------------------------
def extract_fields(text):
    text_lower = text.lower()
    data = {}

    # Vehicle name
    data["vehicle_name"] = extract_vehicle_name(text)

    # Monthly payment
    monthly_match = re.search(r"£([\d,.]+)\s*\+\s*vat per month", text_lower)
    data["monthly_payment"] = monthly_match.group(1) if monthly_match else "Not Available"

    # Down payment / Initial rental
    down_match = re.search(r"initial rental\s*£([\d,.]+)", text_lower)
    data["down_payment"] = down_match.group(1) if down_match else "Not Available"

    # Lease duration
    term_match = re.search(r"(\d+)\s*month term", text_lower)
    data["lease_term_months"] = term_match.group(1) if term_match else "Not Available"

    # Annual mileage
    mileage_match = re.search(r"annual mileage allowance of\s*(\d+)", text_lower)
    data["annual_mileage"] = mileage_match.group(1) if mileage_match else "Not Available"

    # Excess mileage clause
    data["excess_mileage_clause"] = (
        "Present" if "excess mileage" in text_lower else "Not Available"
    )

    # Maintenance
    if "does not include maintenance" in text_lower:
        data["maintenance_included"] = "No"
    elif "includes maintenance" in text_lower:
        data["maintenance_included"] = "Yes"
    else:
        data["maintenance_included"] = "Not Available"

    # Total lease cost
    total_cost_match = re.search(
        r"total cost of lease over the term\s*£([\d,.]+)", text_lower
    )
    data["total_lease_cost"] = total_cost_match.group(1) if total_cost_match else "Not Available"

    # Vehicle details
    fuel_match = re.search(r"fuel type\s*([a-z]+)", text_lower)
    data["fuel_type"] = fuel_match.group(1).capitalize() if fuel_match else "Not Available"

    trans_match = re.search(r"transmission\s*([a-z]+)", text_lower)
    data["transmission"] = trans_match.group(1).capitalize() if trans_match else "Not Available"

    co2_match = re.search(r"co2\s*(\d+)\s*g/km", text_lower)
    data["co2_emissions"] = f"{co2_match.group(1)} g/km" if co2_match else "Not Available"

    p11d_match = re.search(r"p11d\s*£([\d,.]+)", text_lower)
    data["p11d_value"] = p11d_match.group(1) if p11d_match else "Not Available"

    # Explicitly unavailable fields
    data["not_available_in_document"] = [
        "VIN number",
        "APR / Interest rate",
        "Residual value",
        "Purchase option / Buyout price",
        "Early termination penalties",
        "Late payment fees",
        "Warranty details",
        "Insurance coverage"
    ]

    return data

# ------------------------
# PROCESS ALL TXT FILES
# ------------------------
for file in os.listdir(INPUT_FOLDER):
    if not file.endswith(".txt"):
        continue

    print(f"Filtering: {file}")

    with open(os.path.join(INPUT_FOLDER, file), "r", encoding="utf-8") as f:
        text = f.read()

    # Remove obvious noise: phone numbers, emails, extra whitespace
    text_cleaned = re.sub(r"\b\d{5,}\b", "", text)  # phone numbers / long numbers
    text_cleaned = re.sub(r"\S+@\S+", "", text_cleaned)  # emails

    extracted_data = extract_fields(text_cleaned)

    output_file = file.replace(".txt", ".json")
    output_path = os.path.join(OUTPUT_FOLDER, output_file)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=4)

print("\n All contracts filtered successfully!")
