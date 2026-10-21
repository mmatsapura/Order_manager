from datetime import datetime, timezone

from pydantic import BaseModel, EmailStr, Field


class UserProfile(BaseModel):
    first_name: str
    last_name: str
    avatar_url: (str | None) = None


class User(BaseModel):
    id: (str | None) = None
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    profile: (UserProfile | None) = None
    created_at: datetime = Field(default_factory=lambda : datetime.now(timezone.utc))
