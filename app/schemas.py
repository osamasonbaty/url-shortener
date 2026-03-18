from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: str


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(json_schema_extra={"format": "password"})


class UserPublic(BaseModel):
    id: int
    name: str
    email: str


class UserUpdateMe(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = Field(
        default=None,
        json_schema_extra={"format": "password"},
    )


class URLPublic(BaseModel):
    code: str
    url: str
    domain: str
    is_active: bool
    created_at: datetime


class URLCreateResponse(BaseModel):
    url_code: str
    url: str
    domain: str
    is_active: bool
    short_url: str


class URLUpdate(BaseModel):
    url: str


class FilterParams(BaseModel):
    limit: Annotated[int, Field(100, gt=0, le=100)]
    skip: Annotated[int, Field(0, ge=0)]
    asc: bool = False
