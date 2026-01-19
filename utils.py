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
