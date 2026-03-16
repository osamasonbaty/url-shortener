from typing import Annotated

from fastapi import Body, APIRouter, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from pydantic import AnyHttpUrl

from app.api.deps import SessionDep, CurrentUser
from app.services import urls as url_services
from app.schemas import FilterParams

router = APIRouter(prefix="/urls", tags=["urls"])
redirect_router = APIRouter(tags=["urls"])

@router.post("")
def create_url(
    url: Annotated[AnyHttpUrl, Body()],
    db: SessionDep,
    user: CurrentUser
):
    try:
        return url_services.create_url(db=db, user=user, url=url)
    except url_services.UrlCodeGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.get("")
def list_urls(
    db: SessionDep,
    user: CurrentUser,
    filters: Annotated[FilterParams, Query()]
):
    return url_services.list_urls(db=db, user=user, limit=filters.limit, skip=filters.skip, asc=filters.asc)


@router.get("/visits")
def list_url_visits(
    db: SessionDep,
    user: CurrentUser,
    filters: Annotated[FilterParams, Query()]
):
    return url_services.list_url_visits(db=db, user=user, limit=filters.limit, skip=filters.skip, asc=filters.asc)


@redirect_router.get("/{url_code}", response_class=RedirectResponse)
def redirect_to_url(
    url_code: str,
    db: SessionDep
):
    try:
        url = url_services.resolve_redirect_url(db=db, url_code=url_code)
    except url_services.UrlCodeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return RedirectResponse(
        url=url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )
