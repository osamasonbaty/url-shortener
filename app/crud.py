from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserRegister
from app.core.security import verify_password, get_password_hash


def create_user(db: Session, user_create: UserRegister) -> User:
    new_user = User(
        name=user_create.name,
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    user = db.execute(statement).scalars().first()
    return user


def get_user_by_id(db: Session, id: int) -> User | None:
    return db.get(User, id)


# Dummy hash to use for timing attack prevention when user is not found
# This is an Argon2 hash of a random password, used to ensure constant-time comparison
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$m2VO3LXylA0Q7wCQ0azxig$Zkh9IrSHYBaQ9yK+yRCSj185J5xHn7FPb7hOUvpcPAE"


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None:
        # Prevent timing attacks by running password verification even when user doesn't exist
        # This ensures the response time is similar whether or not the email exists
        verify_password(password, DUMMY_HASH)
        return None
    # TODO: Updated password hash with each authentication
    if not verify_password(password, user.hashed_password):
        return None
    return user
