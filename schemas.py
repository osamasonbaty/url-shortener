from pydantic import BaseModel, Field, EmailStr, BeforeValidator
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from typing import Annotated


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: str


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(json_schema_extra={"format": "password"})
    phone: Annotated[
        PhoneNumber | None,
        BeforeValidator(lambda phone: None if phone == "" else phone),
    ] = None
