from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from app.models.user import UserRole
import re


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    username: str
    display_name: str | None
    avatar_url: str | None
    bio: str | None
    role: UserRole
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    username: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(v) > 60:
            raise ValueError("Username must be 60 characters or fewer")
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        return v

    @field_validator("display_name")
    @classmethod
    def display_name_valid(cls, v: str | None) -> str | None:
        if v is not None and len(v.strip()) > 120:
            raise ValueError("Display name must be 120 characters or fewer")
        return v.strip() if v else v

    @field_validator("bio")
    @classmethod
    def bio_valid(cls, v: str | None) -> str | None:
        if v is not None and len(v.strip()) > 500:
            raise ValueError("Bio must be 500 characters or fewer")
        return v.strip() if v else v
