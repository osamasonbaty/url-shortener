from fastapi import FastAPI, Body, HTTPException, Depends
from fastapi.responses import RedirectResponse
from typing import Annotated
from pydantic import AnyHttpUrl
from utils import generate_url_code

from sqlalchemy import Connection, text
from sqlalchemy.exc import IntegrityError
from db.database import Base, engine, get_connection
from db import models


BASE_URL = "http://127.0.0.1:8000/"
MAX_RETRIES = 3

app = FastAPI()

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.post("/urls")
def shorten_url(
    url: Annotated[AnyHttpUrl, Body()],
    conn: Connection = Depends(get_connection)
):
    for _ in range(MAX_RETRIES):
        url_code = generate_url_code()
        try:
            conn.execute(
                text("INSERT INTO urls (code, url) VALUES (:code, :url)"),
                {"code": url_code, "url": str(url)}
            )
            conn.commit()
            return {
                "code": url_code,
                "url": url,
                "short_url": BASE_URL + url_code
            }
        except IntegrityError:
            conn.rollback()
            continue
    raise HTTPException(500, "Failed to generate unique code after maximum retries.")


@app.get("/urls")
def list_urls(conn: Connection = Depends(get_connection)):
    result = conn.execute(
        text("SELECT * FROM urls")
    )
    return result.mappings().all()

@app.get("/{url_code}")
def redirect_to_url(
    url_code: str,
    conn: Connection = Depends(get_connection)
):
    result = conn.execute(
        text("SELECT url FROM urls WHERE code = :code"),
        {"code": url_code}
    )
    rows = result.all()
    if not rows:
        raise HTTPException(404, "URL Code not found")
    
    conn.execute(
        text("INSERT INTO visits (code) VALUES (:code)"),
        {"code": url_code}
    )
    conn.commit()
    
    return RedirectResponse(rows[0].url)

"""
TO DO:
- Assign users
- Get urls per user
- Get the code by url
- Get URL by code (not redirect)
"""