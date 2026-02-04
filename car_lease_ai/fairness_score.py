"""
Fairness Score Module - Evaluates car lease contract transparency
Returns detailed breakdown with score/max structure for each category
"""

from utils import is_missing

def compute_fairness_score(lease: dict) -> dict:
    """
    Computes a fairness score (0-100) for a car lease contract.
    
    Args:
        lease: Dictionary containing extracted lease details
        
    Returns:
        Dictionary with fairness_score, category, breakdown, and warnings
    """
    print("\n" + "="*80)
    print("🔍 FAIRNESS SCORE COMPUTATION STARTED")
    print("="*80)
    
    score = 100
    breakdown = {}
    warnings = []

    # Extract sections from lease data
    payments = lease.get("5. Payment Details", {})
    upfront = payments.get("5.1 Upfront / Signing Payments", {})
    recurring = payments.get("5.2 Recurring Payments", {})
    terms = lease.get("4. Lease Terms / Agreement Details", {})
    vehicle = lease.get("3. Vehicle Specifications", {})
    taxes = lease.get("6. Taxes & Additional Fees", {})
    residual = lease.get("7. Residual & End-of-Lease Details", {})
    
    print(f"📦 Extracted Sections:")
    print(f"   - Payments: {bool(payments)}")
    print(f"   - Terms: {bool(terms)}")
    print(f"   - Vehicle: {bool(vehicle)}")
    print(f"   - Taxes: {bool(taxes)}")
    print(f"   - Residual: {bool(residual)}")
    print("="*80 + "\n")

    # ========================================================================
    # 1️⃣ COST TRANSPARENCY (35 points)
    # ========================================================================
    cost_score = 35
    
    if is_missing(recurring.get("Monthly Payments")):
        cost_score -= 15
        warnings.append("Monthly payment amount not clearly stated")
    
    if is_missing(recurring.get("Total of Payments")):
        cost_score -= 10
        warnings.append("Total cost over lease term not disclosed")
    
    if is_missing(upfront.get("Down Payment")) and is_missing(upfront.get("Capitalized Cost Reduction")):
        cost_score -= 10
        warnings.append("Initial payment requirements unclear")

    breakdown["Cost Transparency"] = cost_score
    score -= (35 - cost_score)

    # ========================================================================
    # 2️⃣ MILEAGE FAIRNESS (25 points)
    # ========================================================================
    mileage_score = 25
    
    if is_missing(terms.get("Agreement Duration / Term Period")):
        mileage_score -= 10
        warnings.append("Lease duration not specified")
    
    if is_missing(terms.get("Mileage Allowance")):
        mileage_score -= 10
        warnings.append("Annual mileage allowance not clear")
    
    # Check for excess mileage charges
    excess_mileage_info = str(taxes.get("Excess Mileage Charge", "")).lower()
    if "information not available" in excess_mileage_info or not excess_mileage_info:
        mileage_score -= 5
        warnings.append("Excess mileage charges not disclosed")

    breakdown["Mileage Fairness"] = mileage_score
    score -= (25 - mileage_score)

    # ========================================================================
    # 3️⃣ TERMINATION CLARITY (20 points)
    # ========================================================================
    termination_score = 20
    
    if is_missing(terms.get("Early Termination Fee")):
        termination_score -= 10
        warnings.append("Early termination fee not specified")
    
    if is_missing(terms.get("Termination Date")):
        termination_score -= 10
        warnings.append("Termination date not specified")

    breakdown["Termination Clarity"] = termination_score
    score -= (20 - termination_score)

    # ========================================================================
    # 4️⃣ RESIDUAL LOGIC (20 points)
    # ========================================================================
    residual_score = 20
    
    # Vehicle identification (10 points)
    vehicle_id = lease.get("2. Vehicle Identification & Basic Details", {})
    if is_missing(vehicle_id.get("Car Name / Model")):
        residual_score -= 5
        warnings.append("Vehicle make/model not clearly identified")
    
    if is_missing(vehicle.get("Body Type")) and is_missing(vehicle.get("Fuel Type")):
        residual_score -= 5
        warnings.append("Vehicle specifications incomplete")
    
    # Residual value (10 points)
    if is_missing(residual.get("Residual Value")):
        residual_score -= 10
        warnings.append("Residual value not disclosed")

    breakdown["Residual Logic"] = residual_score
    score -= (20 - residual_score)

    # ========================================================================
    # 5️⃣ LEGAL CLARITY (15 points)
    # ========================================================================
    legal_score = 15
    
    maintenance_info = str(terms.get("Maintenance Responsibility", "")).lower()
    if "information not available" in maintenance_info or not maintenance_info:
        legal_score -= 5
        warnings.append("Maintenance responsibility unclear")
    
    insurance_info = str(terms.get("Insurance Management Requirements", "")).lower()
    if "information not available" in insurance_info or not insurance_info:
        legal_score -= 5
        warnings.append("Insurance requirements not specified")
    
    vat_info = taxes.get("VAT / Sales Tax", "")
    if is_missing(vat_info):
        legal_score -= 5
        warnings.append("Tax information not clearly stated")

    breakdown["Legal Clarity"] = legal_score
    score -= (15 - legal_score)

    # ========================================================================
    # FINAL SCORE CALCULATION
    # ========================================================================
    final_score = max(score, 0)
    
    # Determine category and risk level
    if final_score >= 85:
        category = "Excellent"
        risk_level = "Low Risk"
    elif final_score >= 70:
        category = "Good"
        risk_level = "Low to Moderate Risk"
    elif final_score >= 55:
        category = "Fair"
        risk_level = "Moderate Risk"
    elif final_score >= 40:
        category = "Needs Review"
        risk_level = "High Risk"
    else:
        category = "Poor"
        risk_level = "Very High Risk"

    # ========================================================================
    # BUILD RESPONSE (with score/max structure for frontend)
    # ========================================================================
    result = {
        "fairness_score": final_score,
        "category": category,
        "risk_level": risk_level,
        "breakdown": {
            "Cost Transparency": {
                "score": breakdown.get("Cost Transparency", 0),
                "max": 35
            },
            "Mileage Fairness": {
                "score": breakdown.get("Mileage Fairness", 0),
                "max": 25
            },
            "Termination Clarity": {
                "score": breakdown.get("Termination Clarity", 0),
                "max": 20
            },
            "Residual Logic": {
                "score": breakdown.get("Residual Logic", 0),
                "max": 20
            },
            "Legal Clarity": {
                "score": breakdown.get("Legal Clarity", 0),
                "max": 15
            }
        },
        "warnings": warnings,
        "max_possible_score": 100,
        "interpretation": _get_interpretation(final_score)
    }
    
    # ========================================================================
    # DEBUG OUTPUT
    # ========================================================================
    print("\n" + "="*80)
    print("✅ FAIRNESS SCORE COMPLETED")
    print("="*80)
    print(f"Final Score: {final_score}/100 ({category})")
    print(f"Risk Level: {risk_level}")
    print(f"\nBreakdown:")
    for key, val in result["breakdown"].items():
        percentage = (val['score'] / val['max'] * 100) if val['max'] > 0 else 0
        print(f"  • {key}: {val['score']}/{val['max']} ({percentage:.0f}%)")
    print(f"\nWarnings: {len(warnings)}")
    for warning in warnings:
        print(f"  ⚠️  {warning}")
    print("="*80 + "\n")
    
    return result


def _get_interpretation(score: int) -> str:
    """Returns a human-readable interpretation of the fairness score."""
    if score >= 85:
        return "This contract is highly transparent with clear terms and comprehensive disclosure."
    elif score >= 70:
        return "This contract has good transparency with most key terms clearly stated."
    elif score >= 55:
        return "This contract has fair transparency but some important details may be unclear."
    elif score >= 40:
        return "This contract lacks clarity in several important areas. Seek clarification before signing."
    else:
        return "This contract has significant transparency issues. Professional review strongly recommended."