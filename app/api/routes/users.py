from typing import Annotated

from fastapi import APIRouter, HTTPException, Form, Response, status
from sqlalchemy.exc import IntegrityError

from app import crud
from app.schemas import UserPublic, UserRegister, UserUpdateMe
from app.api.deps import CurrentUser, SessionDep

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/singnup", response_model=UserPublic)
def register_user(db: SessionDep, user_in: Annotated[UserRegister, Form()]):
    user = crud.get_user_by_email(db, user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already exists")
    user = crud.create_user(db, user_in)

    return user


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser):
    return current_user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    db: SessionDep,
    current_user: CurrentUser,
    user_in: UserUpdateMe,
):
    try:
        return crud.update_user(db, current_user, user_in)
    except IntegrityError as exc:
        raise HTTPException(status_code=400, detail="Email already exists") from exc


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_me(db: SessionDep, current_user: CurrentUser) -> Response:
    crud.delete_user(db, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
