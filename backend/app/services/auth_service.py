from __future__ import annotations

from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from ..auth_models import RefreshTokenSession
from ..models import User, UserRole
from ..schemas.auth import TokenPair


def authenticate_user(session: Session, email: str, password: str) -> User:
    user = session.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return user


def issue_token_pair(session: Session, user: User) -> TokenPair:
    token_id = token_urlsafe(32)
    refresh_expiry = datetime.now(timezone.utc) + timedelta(days=30)
    refresh_session = RefreshTokenSession(user_id=user.id, jti=token_id, token_type="refresh", expires_at=refresh_expiry)
    session.add(refresh_session)
    session.flush()

    return TokenPair(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id), token_id),
    )


def rotate_refresh_token(session: Session, refresh_token: str) -> TokenPair:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh" or not payload.get("jti"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    token_session = session.scalar(select(RefreshTokenSession).where(RefreshTokenSession.jti == payload["jti"]))
    if token_session is None or token_session.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")

    if _as_utc(token_session.expires_at) < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    user = session.get(User, int(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    token_session.revoked_at = datetime.now(timezone.utc)
    return issue_token_pair(session, user)


def revoke_refresh_token(session: Session, refresh_token: str) -> None:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh" or not payload.get("jti"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    token_session = session.scalar(select(RefreshTokenSession).where(RefreshTokenSession.jti == payload["jti"]))
    if token_session is None:
        return
    token_session.revoked_at = datetime.now(timezone.utc)


def create_user(session: Session, *, name: str, email: str, password: str, role: UserRole) -> User:
    existing_user = session.scalar(select(User).where(User.email == email))
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(name=name, email=email, password_hash=hash_password(password), role=role)
    session.add(user)
    session.flush()
    return user


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
