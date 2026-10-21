from pydantic import BaseModel, ConfigDict, Field, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=32)


class UserPublic(BaseModel):
    id: str
    email: str

    model_config = ConfigDict(from_attributes=True)
