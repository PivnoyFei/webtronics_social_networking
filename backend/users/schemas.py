import datetime
from typing import Any

from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, Field, root_validator, validator


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
    sub: int
    exp: int


class TokenBase(BaseModel):
    refresh_token: str = Field(...)


class UserPassword(UserOut):
    password: str


class SetPassword(BaseModel):
    current_password: str = Field(..., description="old password")
    new_password: str = Field(..., description="New Password")

    @root_validator()
    def validator(cls, value: Any) -> Any:
        if value["current_password"] == value["new_password"]:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Incorrect password"
            )
        return value
