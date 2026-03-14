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