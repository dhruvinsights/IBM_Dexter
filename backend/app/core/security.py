"""Security utilities for authentication and request validation."""

from datetime import datetime, timedelta, timezone
import hmac
import logging
from typing import Any, Dict, Optional

from fastapi import Header, HTTPException, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

logger = logging.getLogger(__name__)
_settings = get_settings()
# bcrypt can fail to initialize on some developer/CI images; use pbkdf2 for automated tests only.
_hash_scheme = "pbkdf2_sha256" if _settings.app_env == "test" else "bcrypt"
pwd_context = CryptContext(schemes=[_hash_scheme], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")
api_key_scheme = APIKeyHeader(name=_settings.api_key_header_name, auto_error=False)


def hash_password(password: str) -> str:
    """Hash a plain text password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


def _build_token(subject: str, expires_delta: timedelta, token_type: str) -> str:
    """Create a signed JWT token for the given subject."""
    now = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return jwt.encode(payload, _settings.jwt_secret_key, algorithm=_settings.jwt_algorithm)


def create_access_token(subject: str) -> str:
    """Create a short-lived access token."""
    return _build_token(
        subject=subject,
        expires_delta=timedelta(minutes=_settings.access_token_expire_minutes),
        token_type="access",
    )


def create_refresh_token(subject: str) -> str:
    """Create a long-lived refresh token."""
    return _build_token(
        subject=subject,
        expires_delta=timedelta(minutes=_settings.refresh_token_expire_minutes),
        token_type="refresh",
    )


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token."""
    try:
        return jwt.decode(token, _settings.jwt_secret_key, algorithms=[_settings.jwt_algorithm])
    except JWTError as exc:
        logger.warning("Token validation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from exc


def validate_token_type(payload: Dict[str, Any], expected_type: str) -> None:
    """Validate a decoded token type."""
    if payload.get("type") != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type. Expected {expected_type}.",
        )


async def validate_api_key(
    api_key: Optional[str] = Security(api_key_scheme),
    x_signature: Optional[str] = Header(default=None),
) -> str:
    """Validate an API key or signature-based request."""
    if api_key and hmac.compare_digest(api_key, _settings.api_key):
        return api_key
    if x_signature and hmac.compare_digest(x_signature, _settings.api_key):
        return x_signature
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")

# Made with Bob
