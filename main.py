from fastapi import FastAPI, Body, HTTPException, Depends, status
from fastapi.responses import RedirectResponse
from typing import Annotated
from pydantic import AnyHttpUrl
from utils import generate_url_code

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from db.database import Base, engine, get_db
from db.models import URL, Visit


BASE_URL = "http://127.0.0.1:8000/"
MAX_RETRIES = 3

app = FastAPI()

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.post("/urls")
def shorten_url(
    url: Annotated[AnyHttpUrl, Body()],
    db: Session = Depends(get_db)
):
    for _ in range(MAX_RETRIES):
        url_code = generate_url_code()
        try:
            db.add(
                URL(code=url_code, url=str(url))
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
def list_urls(db: Session = Depends(get_db)):
    stmt = select(URL)
    return db.execute(stmt).scalars().all()

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

"""
TO DO:
- Assign users
- Get urls per user
- Get the code by url
- Get URL by code (not redirect)
"""