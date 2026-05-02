from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.user import UserRole


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
    display_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
