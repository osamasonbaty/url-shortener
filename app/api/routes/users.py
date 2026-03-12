from typing import Annotated

from fastapi import APIRouter, HTTPException, Form

from app import crud
from app.schemas import UserPublic, UserRegister
from app.api.deps import SessionDep

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/singup", response_model=UserPublic)
def register_user(db: SessionDep, user_in: Annotated[UserRegister, Form()]):
    user = crud.get_user_by_email(db, user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already exists")
    user = crud.create_user(db, user_in)

    return user