import datetime

import bcrypt
import jwt
from core.config import (
    JWT_PRIVATE_KEY,
    JWT_PUBLIC_KEY,
    JWT_ALGORITHM,
    JWT_EXPIRE_MINUTES,
)


# Хэширование пароля
def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


# Проверка пароля
def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password)


# Генерация JWT токена
def encode_jwt(payload: dict, expire_minutes: int = JWT_EXPIRE_MINUTES) -> str:
    now = datetime.datetime.utcnow()
    expire = now + datetime.timedelta(minutes=expire_minutes)
    payload.update({"exp": expire, "iat": now})
    return jwt.encode(payload, JWT_PRIVATE_KEY, algorithm=JWT_ALGORITHM)


# Декодирование JWT токена
def decode_jwt(token: str) -> dict:
    return jwt.decode(token, JWT_PUBLIC_KEY, algorithms=[JWT_ALGORITHM])