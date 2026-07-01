from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...api.deps import get_database_session, require_roles
from ...models import User, UserRole
from ...schemas.users import UserCreate, UserRead, UserUpdate
from ...services.auth_service import create_user


router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead], dependencies=[Depends(require_roles(UserRole.ADMIN))])
def list_users(session: Session = Depends(get_database_session)) -> list[User]:
    return list(session.scalars(select(User).order_by(User.id)).all())


@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(require_roles(UserRole.ADMIN))])
def get_user(user_id: int, session: Session = Depends(get_database_session)) -> User:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(UserRole.ADMIN))])
def create_user_endpoint(payload: UserCreate, session: Session = Depends(get_database_session)) -> User:
    user = create_user(
        session,
        name=payload.name,
        email=payload.email,
        password=payload.password,
        role=payload.role,
    )
    session.commit()
    return user


@router.put("/{user_id}", response_model=UserRead, dependencies=[Depends(require_roles(UserRole.ADMIN))])
def update_user(user_id: int, payload: UserUpdate, session: Session = Depends(get_database_session)) -> User:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.name is not None:
        user.name = payload.name
    if payload.email is not None:
        duplicate = session.scalar(select(User).where(User.email == payload.email, User.id != user_id))
        if duplicate is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        user.email = payload.email
    if payload.role is not None:
        user.role = payload.role
    if payload.password is not None:
        from ...core.security import hash_password

        user.password_hash = hash_password(payload.password)

    session.commit()
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles(UserRole.ADMIN))])
def delete_user(user_id: int, session: Session = Depends(get_database_session)) -> None:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    session.delete(user)
    session.commit()
