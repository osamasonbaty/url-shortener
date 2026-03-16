import secrets
import string
from typing import Any

from pydantic import AnyHttpUrl
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import array_agg
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


def list_urls(
    db: Session,
    user: User,
    limit: int | None = None,
    skip: int | None = None,
    asc: bool = False,
):
    order = URL.created_at.asc() if asc else URL.created_at.desc()
    stmt = select(URL.code, URL.created_at).where(URL.user_id == user.id).order_by(order)
    if skip is not None:
        stmt = stmt.offset(skip)
    if limit is not None:
        stmt = stmt.limit(limit)
    rows = db.execute(stmt).mappings().all()
    return rows


# This is codex spagetti code
def list_url_visits(
    db: Session,
    user: User,
    limit: int | None = None,
    skip: int | None = None,
    asc: bool = False,
) -> list[dict]:
    visit_count = func.count(Visit.id)
    visit_dates = array_agg(Visit.created_at, order_by=Visit.created_at.desc()).filter(
        Visit.id.is_not(None)
    )
    order = visit_count.asc() if asc else visit_count.desc()
    stmt = (
        select(
            URL.code.label("url_code"),
            visit_count.label("visit_count"),
            visit_dates.label("visit_dates"),
        )
        .outerjoin(Visit, Visit.code == URL.code)
        .where(URL.user_id == user.id)
        .group_by(URL.code)
        .order_by(order)
    )
    if skip is not None:
        stmt = stmt.offset(skip)
    if limit is not None:
        stmt = stmt.limit(limit)
    rows = db.execute(stmt).mappings().all()
    return [
        {
            "url_code": row["url_code"],
            "visit_count": row["visit_count"],
            "visit_dates": row["visit_dates"] or [],
        }
        for row in rows
    ]


def resolve_redirect_url(db: Session, url_code: str) -> str:
    stmt = select(URL.url).where(URL.code == url_code)
    url = db.execute(stmt).scalar_one_or_none()

    if url is None:
        raise UrlCodeNotFoundError("URL code not found")

    db.add(Visit(code=url_code))
    db.commit()

    return url
