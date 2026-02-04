from app.utils.auth import hash_password

users_db = {}

def create_user(email: str, password: str):
    if email in users_db:
        return None

    users_db[email] = {
        "email": email,
        "password": hash_password(password)
    }
    return users_db[email]

def get_user(email: str):
    return users_db.get(email)
