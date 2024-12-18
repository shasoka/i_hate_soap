import datetime

import bcrypt
import jwt
from jwt import InvalidTokenError
from spyne import Fault, InvalidCredentialsError
from spyne.service import Service
from twisted.python import log

from core.config import (
    JWT_PRIVATE_KEY,
    JWT_PUBLIC_KEY,
    JWT_ALGORITHM,
    JWT_EXPIRE_MINUTES,
)
from core.db.models import User

AuthFault: Fault = InvalidCredentialsError("Login or password is invalid")
CredentialsFault: Fault = InvalidCredentialsError("Unathorized")


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


def _get_current_auth_user(ctx: Service, token: str) -> User:
    if token is None:
        raise CredentialsFault

    if isinstance(token, str):
        if token.startswith("Bearer "):
            token = token[7:]

        try:
            payload: dict = decode_jwt(token)
        except InvalidTokenError:
            raise CredentialsFault

        return (
            ctx.udc.session.query(User)
            .filter(User.id == int(payload["sub"]))
            .first()
        )


def authenticate_user(ctx: Service) -> User:
    try:
        return _get_current_auth_user(
            ctx, ctx.in_header.Authorization if ctx.in_header else None
        )
    except Exception:
        log.msg("[AUTH] User authentication failed.")
        raise
