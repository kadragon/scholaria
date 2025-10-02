"""Initial setup endpoints for first-time admin creation."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.auth.utils import pwd_context
from backend.models.base import get_db
from backend.models.user import User

router = APIRouter(prefix="/setup", tags=["Setup"])


class SetupCheckResponse(BaseModel):
    needs_setup: bool
    admin_exists: bool


class InitialAdminCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8)


class InitialAdminResponse(BaseModel):
    id: int
    username: str
    email: str
    message: str


@router.get("/check", response_model=SetupCheckResponse)
async def check_setup_status(
    db: Annotated[Session, Depends(get_db)],
) -> SetupCheckResponse:
    admin_count = (
        db.query(func.count(User.id))
        .filter(
            User.is_staff == True  # noqa: E712
        )
        .scalar()
    )

    admin_exists = admin_count > 0

    return SetupCheckResponse(
        needs_setup=not admin_exists,
        admin_exists=admin_exists,
    )


@router.post(
    "/init",
    response_model=InitialAdminResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_initial_admin(
    data: InitialAdminCreate,
    db: Annotated[Session, Depends(get_db)],
) -> InitialAdminResponse:
    admin_exists = (
        db.query(func.count(User.id))
        .filter(
            User.is_staff == True  # noqa: E712
        )
        .scalar()
    )

    if admin_exists > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin user already exists. Initial setup is not allowed.",
        )

    username_exists = db.query(User).filter(User.username == data.username).first()
    if username_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    email_exists = db.query(User).filter(User.email == data.email).first()
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )

    admin = User(
        username=data.username,
        email=data.email,
        password=pwd_context.hash(data.password),
        is_active=True,
        is_staff=True,
        is_superuser=True,
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return InitialAdminResponse(
        id=int(admin.id),
        username=str(admin.username),
        email=str(admin.email),
        message="Initial admin user created successfully. Please login with your credentials.",
    )
