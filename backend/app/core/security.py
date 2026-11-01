from datetime import datetime, timedelta, timezone
from typing import Any, Literal

import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
TokenType = Literal["access", "refresh"]


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_token(subject: str, token_type: TokenType, extra: dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    ttl = (
        timedelta(minutes=settings.ACCESS_TOKEN_MINUTES)
        if token_type == "access"
        else timedelta(days=settings.REFRESH_TOKEN_DAYS)
    )
    payload = {"sub": subject, "type": token_type, "iat": now, "exp": now + ttl, **(extra or {})}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str, expected_type: TokenType) -> dict[str, Any]:
    """Raises jwt.PyJWTError on bad signature/expiry; ValueError on wrong token type."""
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    if payload.get("type") != expected_type:
        raise ValueError("wrong token type")
    return payload
