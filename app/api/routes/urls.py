from datetime import datetime
from typing import Annotated

from fastapi import Body, HTTPException, status, APIRouter
from fastapi.responses import RedirectResponse
from pydantic import AnyHttpUrl
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.utils import generate_url_code
from app.models import URL, Visit
from app.core.config import settings
from app.api.deps import SessionDep, CurrentUser

router = APIRouter(prefix="/urls", tags=["urls"])
redirect_router = APIRouter(tags=["urls"])

@router.post("")
def create_url(
    url: Annotated[AnyHttpUrl, Body()],
    db: SessionDep,
    user: CurrentUser
):
    for _ in range(settings.CODE_GEN_MAX_RETRIES):
        url_code = generate_url_code()
        try:
            db.add(
                URL(code=url_code, url=str(url), user_id=user.id)
            )
            db.commit()
            return {
                "url_code": url_code,
                "url": url,
                "short_url": f"{settings.BACKEND_HOST}/{url_code}"
            }
        except IntegrityError:
            db.rollback()
            
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to generate unique code after maximum retries"
    )


@router.get("")
def list_urls(
    db: SessionDep,
    user: CurrentUser
):
    stmt = select(URL.code, URL.created_at).where(URL.user_id == user.id)
    rows = db.execute(stmt).mappings().all()
    return rows


@router.get("/visits")
def list_url_visits(
    db: SessionDep,
    user: CurrentUser
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


@redirect_router.get("/{url_code}", response_class=RedirectResponse)
def redirect_to_url(
    url_code: str,
    db: SessionDep
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