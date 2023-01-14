import datetime
from typing import Optional

from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    username: str = Field(..., min_length=5, max_length=25)
    first_name: str
    last_name: str


class UserOut(UserBase):
    id: int
    email: EmailStr
    timestamp: datetime.datetime


class UserCreate(UserBase):
    email: EmailStr
    password: str

    @validator("username", "first_name", "last_name",)
    def validator(cls, value: str) -> str:
        if not value.isalpha():
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, "Unacceptable symbols"
            )
        return value


class UserAuth(BaseModel):
    username: str
    password: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[int] = None


class TokenBase(BaseModel):
    refresh_token: str = Field(...)
