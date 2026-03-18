from typing import Annotated

from fastapi import Body, APIRouter, HTTPException, Response, status, Query
from fastapi.responses import RedirectResponse
from pydantic import AnyHttpUrl

from app.api.deps import SessionDep, CurrentUser
from app.services import urls as url_services
from app.schemas import FilterParams, URLCreateResponse, URLPublic

router = APIRouter(prefix="/urls", tags=["urls"])
redirect_router = APIRouter(tags=["urls"])

@router.post("", response_model=URLCreateResponse)
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


@router.get("", response_model=list[URLPublic])
def list_urls(
    db: SessionDep,
    user: CurrentUser,
    filters: Annotated[FilterParams, Query()]
):
    return url_services.list_urls(db=db, user=user, limit=filters.limit, skip=filters.skip, asc=filters.asc)


@router.get("/domain/{domain}", response_model=list[URLPublic])
def list_urls_by_domain(
    domain: str,
    db: SessionDep,
    user: CurrentUser,
    filters: Annotated[FilterParams, Query()]
):
    return url_services.list_urls_by_domain(
        db=db,
        user=user,
        domain=domain,
        limit=filters.limit,
        skip=filters.skip,
        asc=filters.asc,
    )


@router.get("/visits")
def list_url_visits(
    db: SessionDep,
    user: CurrentUser,
    filters: Annotated[FilterParams, Query()]
):
    return url_services.list_url_visits(db=db, user=user, limit=filters.limit, skip=filters.skip, asc=filters.asc)


@router.patch("/{url_code}", response_model=URLPublic)
def update_own_url(
    url_code: str,
    url: Annotated[AnyHttpUrl, Body()],
    db: SessionDep,
    user: CurrentUser,
):
    try:
        return url_services.update_user_url(db=db, user=user, url_code=url_code, url=url)
    except url_services.UrlCodeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post("/{url_code}/deactivate", response_model=URLPublic)
def deactivate_own_url(
    url_code: str,
    db: SessionDep,
    user: CurrentUser,
):
    try:
        return url_services.deactivate_user_url(db=db, user=user, url_code=url_code)
    except url_services.UrlCodeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post("/{url_code}/reactivate", response_model=URLPublic)
def reactivate_own_url(
    url_code: str,
    db: SessionDep,
    user: CurrentUser,
):
    try:
        return url_services.reactivate_user_url(db=db, user=user, url_code=url_code)
    except url_services.UrlCodeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete("/{url_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_own_url(
    url_code: str,
    db: SessionDep,
    user: CurrentUser,
) -> Response:
    try:
        url_services.delete_user_url(db=db, user=user, url_code=url_code)
    except url_services.UrlCodeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
    except url_services.UrlCodeInactiveError as exc:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=str(exc),
        ) from exc
    return RedirectResponse(
        url=url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )
