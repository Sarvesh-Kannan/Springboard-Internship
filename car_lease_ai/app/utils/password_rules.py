import re

def validate_password(password: str):
    # ❗ Reject non-ASCII characters (bcrypt requirement)
    try:
        password.encode("ascii")
    except UnicodeEncodeError:
        raise ValueError(
            "Password can only contain standard characters. "
            "Avoid emojis or special symbols like ₹, €, or smart quotes."
        )

    if len(password) > 60:
        raise ValueError("Password must be 60 characters or fewer")

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")

    if not any(c.isupper() for c in password):
        raise ValueError("Password must contain an uppercase letter")

    if not any(c.islower() for c in password):
        raise ValueError("Password must contain a lowercase letter")

    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain a number")

    if not any(c in "!@#$%^&*()_+-=[]{}|;:'\",.<>?/`~" for c in password):
        raise ValueError("Password must contain a special character")

