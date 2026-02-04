from utils import is_missing

def detect_red_flags(lease: dict) -> list:
    flags = []

    payments = lease.get("5. Payment Details", {})
    recurring = payments.get("5.2 Recurring Payments", {})
    terms = lease.get("4. Lease Terms / Agreement Details", {})
    residual = lease.get("7. Residual & End-of-Lease Details", {})

    if is_missing(recurring.get("Total of Payments")):
        flags.append("Total cost of lease not clearly disclosed")

    if is_missing(terms.get("Early Termination Fee")):
        flags.append("Early termination fee not specified")

    if is_missing(residual.get("Residual Value")):
        flags.append("Residual value missing")

    if "does not include maintenance" in str(
        terms.get("Maintenance Responsibility", "")
    ).lower():
        flags.append("Maintenance costs borne by lessee")

    disclaimer = str(
        terms.get("Other Terms and Conditions / Disclaimer", "")
    ).lower()
    if "subject to change" in disclaimer:
        flags.append("Pricing subject to unilateral change")

    return flags
