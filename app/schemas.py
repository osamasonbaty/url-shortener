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


class FilterParams(BaseModel):
    limit: Annotated[int, Field(100, gt=0, le=100)]
    skip: Annotated[int, Field(0, ge=0)]
    asc: bool = False