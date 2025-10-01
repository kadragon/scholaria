"""User model for Django auth_user table."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from backend.models.base import Base


class User(Base):
    """User model mapped to Django auth_user table (read-only)."""

    __tablename__ = "auth_user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False, index=True)
    email = Column(String(254), nullable=False, default="")
    password = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_staff = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    first_name = Column(String(150), nullable=False, default="")
    last_name = Column(String(150), nullable=False, default="")
    date_joined = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
