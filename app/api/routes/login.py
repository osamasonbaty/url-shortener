from typing import Annotated
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.schemas import Token
from app.core.config import settings
from app.core.security import create_access_token
from app.api.deps import SessionDep

router = APIRouter(tags=["login"])


@router.post("/login/access-token")
def login_access_token(db: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=create_access_token(str(user.id), access_token_expires),
        token_type="bearer"
    )