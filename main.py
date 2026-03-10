import os
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import FastAPI, Body, Form, HTTPException, Depends, status
from fastapi.responses import RedirectResponse
from utils import generate_url_code
from dotenv import load_dotenv
from pydantic import AnyHttpUrl, ValidationError

from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash

from sqlalchemy import select, exists
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from db.database import Base, engine, get_db
from db.models import URL, Visit, User
from schemas import Token, TokenData, UserRegister

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000/")
MAX_RETRIES = os.getenv("MAX_RETRIES", 3)
ACCESS_TOKEN_EXPIRES_MINUTES= os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES", 30)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

app = FastAPI()

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


######################
###### Security ######
######################
oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummypassword")

def get_hashed_password(password: str):
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    user = db.execute(statement).scalars().first()
    return user

def get_user_by_id(db: Session, id: int) -> User | None:
    statement = select(User).where(User.id == id)
    user = db.execute(statement).scalars().first()
    return user

def create_access_token(sub: str, expires_delta: timedelta):
    expires = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(
        payload={"sub": str(sub), "exp": expires},
        key=SECRET_KEY,
        algorithm=ALGORITHM
    )

def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None:
        verify_password(password, DUMMY_HASH) # prevent timing attacks
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def get_current_user(
        db: Annotated[Session, Depends(get_db)],
        token: Annotated[str, Depends(oauth2_schema)]
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenData(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = db.get(User, int(token_data.sub))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
    
@app.post("/token")
def login_for_access_token(db: Annotated[Session, Depends(get_db)], form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # auhtenticate user
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES) # type: ignore
    return Token(
        access_token=create_access_token(str(user.id), access_token_expires),
        token_type="bearer"
    )


@app.post("/register")
def register(db: Annotated[Session, Depends(get_db)], form_data: Annotated[UserRegister, Form()]):
    email_exists = db.scalar(
        select(exists().where(User.email == form_data.email))
    )
    if email_exists:
        raise HTTPException(status_code=400, detail="Email already exists")
    new_user = User(
        name=form_data.name,
        email=form_data.email,
        hashed_password=get_hashed_password(form_data.password),
        phone=form_data.phone
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"id": new_user.id, "email": new_user.email, "phone": form_data.phone}
######################
### Main Endpoints ###
######################

@app.post("/urls")
def shorten_url(
    url: Annotated[AnyHttpUrl, Body()],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)]
):
    for _ in range(MAX_RETRIES): # type: ignore
        url_code = generate_url_code()
        try:
            db.add(
                URL(code=url_code, url=str(url), user_id=user.id)
            )
            db.commit()
            return {
                "url_code": url_code,
                "url": url,
                "short_url": BASE_URL + url_code
            }
        except IntegrityError:
            db.rollback()
            
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to generate unique code after maximum retries"
    )


@app.get("/urls")
def list_urls(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)]
):
    stmt = select(URL.code, URL.created_at).where(URL.user_id == user.id)
    rows = db.execute(stmt).mappings().all()
    return rows

@app.get("/urls/visits")
def list_url_visits(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)]
):
    stmt = (
        select(URL.code, Visit.created_at)
        .outerjoin(Visit, Visit.code == URL.code)
        .where(URL.user_id == user.id)
        .order_by(URL.code, Visit.created_at)
    )
    rows = db.execute(stmt).all()
    visits_by_code: dict[str, list[datetime]] = {}
    for code, created_at in rows:
        if code not in visits_by_code:
            visits_by_code[code] = []
        if created_at is not None:
            visits_by_code[code].append(created_at)
    return [
        {"code": code, "visits": len(dates), "dates": dates}
        for code, dates in visits_by_code.items()
    ]

@app.get("/{url_code}", response_class=RedirectResponse)
def redirect_to_url(
    url_code: str,
    db: Session = Depends(get_db)
):
    stmt = select(URL.url).where(URL.code == url_code)
    url = db.execute(stmt).scalar_one_or_none()

    if url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL code not found"
        )
    
    db.add(Visit(code=url_code))
    db.commit()
    
    return RedirectResponse(
        url=url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )
