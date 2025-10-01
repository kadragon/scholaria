"""Authentication router: login and user info."""

from __future__ import annotations

from typing import Annotated, cast

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from backend.auth.utils import create_access_token, verify_password
from backend.dependencies.auth import get_current_user
from backend.models.base import get_db
from backend.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


class Token(BaseModel):
    """Token response model."""

    access_token: str
    token_type: str


class UserOut(BaseModel):
    """User output model."""

    id: int
    username: str
    email: str
    is_staff: bool
    is_superuser: bool

    model_config = ConfigDict(from_attributes=True)


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    """Login endpoint: verify credentials and issue JWT token."""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, cast(str, user.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not cast(bool, user.is_active):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserOut)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> UserOut:
    """Get current logged-in user info."""
    return UserOut.model_validate(current_user)
