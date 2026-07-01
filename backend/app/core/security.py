from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import secrets
from typing import Any

from jose import JWTError, jwt

from .config import get_settings


_PBKDF2_ITERATIONS = 210_000
_SALT_BYTES = 16


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(_SALT_BYTES)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        _PBKDF2_ITERATIONS,
    )
    return f"pbkdf2_sha256${_PBKDF2_ITERATIONS}${salt.hex()}${password_hash.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        algorithm, iterations, salt_hex, hash_hex = hashed_password.split("$")
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    expected = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        int(iterations),
    ).hex()
    return hmac.compare_digest(expected, hash_hex)


def create_access_token(subject: str, expires_delta_minutes: int | None = None) -> str:
    settings = get_settings()
    expire_minutes = expires_delta_minutes or settings.access_token_expire_minutes
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": expire, "type": "access"}
    return _encode_token(payload)


def create_refresh_token(subject: str, token_id: str, expires_delta_minutes: int | None = None) -> str:
    settings = get_settings()
    expire_minutes = expires_delta_minutes or (settings.access_token_expire_minutes * 24)
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": expire, "type": "refresh", "jti": token_id}
    return _encode_token(payload)


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise ValueError("Invalid token") from exc

    subject = payload.get("sub")
    token_type = payload.get("type")
    if not subject or token_type not in {"access", "refresh"}:
        raise ValueError("Invalid token payload")
    return payload


def _encode_token(payload: dict[str, Any]) -> str:
    settings = get_settings()
    return jwt.encode(payload, settings.jwt_secret_key.get_secret_value(), algorithm=settings.jwt_algorithm)
