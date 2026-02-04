from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import hashlib

SECRET_KEY = "CHANGE_THIS_TO_A_RANDOM_STRING"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _prehash(password: str) -> bytes:
    """
    Normalize password length safely for bcrypt
    """
    return hashlib.sha256(password.encode("utf-8")).digest()


def hash_password(password: str) -> str:
    return pwd_context.hash(_prehash(password))


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(_prehash(plain), hashed)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
