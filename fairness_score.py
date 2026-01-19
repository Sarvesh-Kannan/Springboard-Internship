from utils import is_missing

def compute_fairness_score(lease: dict) -> dict:
    score = 100
    breakdown = {}

    payments = lease.get("5. Payment Details", {})
    upfront = payments.get("5.1 Upfront / Signing Payments", {})
    recurring = payments.get("5.2 Recurring Payments", {})

    terms = lease.get("4. Lease Terms / Agreement Details", {})
    residual = lease.get("7. Residual & End-of-Lease Details", {})
    taxes = lease.get("6. Taxes & Additional Fees", {})

    # 1️⃣ Cost Transparency (30)
    cost_score = 30
    if is_missing(recurring.get("Monthly Payments")):
        cost_score -= 10
    if is_missing(recurring.get("Total of Payments")):
        cost_score -= 10
    if is_missing(upfront.get("Processing Fee")):
        cost_score -= 5
    if is_missing(taxes.get("VAT / Sales Tax")):
        cost_score -= 5

    breakdown["cost_transparency"] = cost_score
    score -= (30 - cost_score)

    # 2️⃣ Mileage Fairness (20)
    mileage_score = 20
    if is_missing(terms.get("Mileage Allowance")):
        mileage_score -= 10
    if "excess mileage" not in str(taxes).lower():
        mileage_score -= 10

    breakdown["mileage_fairness"] = mileage_score
    score -= (20 - mileage_score)

    # 3️⃣ Termination Clarity (20)
    termination_score = 20
    if is_missing(terms.get("Early Termination Fee")):
        termination_score -= 10

    breakdown["termination_clarity"] = termination_score
    score -= (20 - termination_score)

    # 4️⃣ Residual & Depreciation (15)
    residual_score = 15
    if is_missing(residual.get("Residual Value")):
        residual_score -= 10
    if is_missing(lease.get("3. Vehicle Specifications", {})
                 .get("Vehicle Depreciation Rate per Month")):
        residual_score -= 5

    breakdown["residual_logic"] = residual_score
    score -= (15 - residual_score)

    # 5️⃣ Legal Clarity (15)
    legal_score = 15
    if is_missing(terms.get("Maintenance Responsibility")):
        legal_score -= 5
    if is_missing(terms.get("Insurance Management Requirements")):
        legal_score -= 5
    if is_missing(terms.get("Other Terms and Conditions / Disclaimer")):
        legal_score -= 5

    breakdown["legal_clarity"] = legal_score
    score -= (15 - legal_score)

    return {
        "fairness_score": max(score, 0),
        "category": (
            "Fair" if score >= 80 else
            "Needs Review" if score >= 60 else
            "High Risk"
        ),
        "breakdown": breakdown
    }
