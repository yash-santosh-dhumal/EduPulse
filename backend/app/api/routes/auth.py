from fastapi import APIRouter, Depends, Response, status, Request
from sqlalchemy.orm import Session
from ...core.rate_limit import limiter

from ...api.deps import get_current_user, get_database_session
from ...models import User
from ...schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, TokenPair
from ...schemas.users import UserRead
from ...services.auth_service import authenticate_user, issue_token_pair, revoke_refresh_token, rotate_refresh_token


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenPair)
@limiter.limit("5/minute")
def login(request: Request, payload: LoginRequest, session: Session = Depends(get_database_session)) -> TokenPair:
	user = authenticate_user(session, payload.email, payload.password)
	token_pair = issue_token_pair(session, user)
	session.commit()
	return token_pair


@router.post("/refresh", response_model=TokenPair)
@limiter.limit("20/minute")
def refresh(request: Request, payload: RefreshRequest, session: Session = Depends(get_database_session)) -> TokenPair:
	token_pair = rotate_refresh_token(session, payload.refresh_token)
	session.commit()
	return token_pair


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: LogoutRequest, session: Session = Depends(get_database_session)) -> Response:
	revoke_refresh_token(session, payload.refresh_token)
	session.commit()
	return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserRead)
def current_user(user: User = Depends(get_current_user)) -> User:
	return user