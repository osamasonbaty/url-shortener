import secrets
import string
from typing import Any

from pydantic import AnyHttpUrl
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import URL, Visit, User


class UrlServiceError(Exception):
    pass


class UrlCodeNotFoundError(UrlServiceError):
    pass


class UrlCodeGenerationError(UrlServiceError):
    pass


ALPHABET = string.ascii_letters + string.digits  # a-zA-Z0-9


def generate_url_code(length: int = 6) -> str:
    if length <= 0:
        raise ValueError("Length must be positive")

    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def create_url(db: Session, user: User, url: AnyHttpUrl) -> dict[str, Any]:
    for _ in range(settings.CODE_GEN_MAX_RETRIES):
        url_code = generate_url_code()
        try:
            db.add(URL(code=url_code, url=str(url), user_id=user.id))
            db.commit()
            return {
                "url_code": url_code,
                "url": url,
                "short_url": f"{settings.BACKEND_HOST}/{url_code}",
            }
        except IntegrityError:
            db.rollback()

    raise UrlCodeGenerationError(
        "Failed to generate unique code after maximum retries",
    )


def list_urls(db: Session, user: User):
    stmt = select(URL.code, URL.created_at).where(URL.user_id == user.id)
    rows = db.execute(stmt).mappings().all()
    return rows


def list_url_visits(db: Session, user: User):
    stmt = select(URL).where(URL.user_id == user.id)
    urls = db.execute(stmt).scalars().all()

    return [
        {
            "url_code": url.code,
            "visit_count": len(url.visits),
            "visit_dates": [visit.created_at for visit in url.visits],
        }
        for url in urls
    ]


def resolve_redirect_url(db: Session, url_code: str) -> str:
    stmt = select(URL.url).where(URL.code == url_code)
    url = db.execute(stmt).scalar_one_or_none()

    if url is None:
        raise UrlCodeNotFoundError("URL code not found")

    db.add(Visit(code=url_code))
    db.commit()

    return url
