import re

def is_valid_vin(vin: str) -> bool:
    return bool(re.match(r"^[A-HJ-NPR-Z0-9]{17}$", vin.upper()))

def is_missing(value):
    if value is None:
        return True
    if isinstance(value, str) and value.strip().lower() in [
        "information not available",
        "not available",
        "n/a",
        ""
    ]:
        return True
    return False

