import jwt
from fastapi import APIRouter, Cookie, Response
from sqlalchemy import select

from app.api.deps import DB, CurrentUser
from app.core.config import settings
from app.core.exceptions import Unauthorized
from app.core.permissions import permissions_for
from app.core.security import create_token, decode_token, verify_password
from app.models import User
from app.schemas.auth import LoginIn, MeOut, TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])
REFRESH_COOKIE = "vrptw_refresh"


def _me(user: User) -> MeOut:
    # User has no `permissions` attribute, so validate the base fields first and add permissions explicitly.
    return MeOut(**UserOut.model_validate(user).model_dump(), permissions=sorted(permissions_for(user.role)))


def _issue(user: User, response: Response) -> TokenOut:
    response.set_cookie(REFRESH_COOKIE, create_token(user.id, "refresh"), httponly=True, secure=True,
                        samesite="strict", max_age=settings.REFRESH_TOKEN_DAYS * 86400, path="/api/v1/auth")
    return TokenOut(access_token=create_token(user.id, "access", {"role": user.role}),
                    expires_in=settings.ACCESS_TOKEN_MINUTES * 60, user=_me(user))


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, response: Response, db: DB):
    user = db.scalar(select(User).where(User.email == data.email))
    if not user or not user.is_active or not verify_password(data.password, user.password_hash):
        raise Unauthorized("Invalid email or password", code="BAD_CREDENTIALS")
    return _issue(user, response)


@router.post("/refresh", response_model=TokenOut)
def refresh(response: Response, db: DB, vrptw_refresh: str | None = Cookie(default=None)):
    if not vrptw_refresh:
        raise Unauthorized("No refresh token")
    try:
        payload = decode_token(vrptw_refresh, "refresh")
    except (jwt.PyJWTError, ValueError):
        raise Unauthorized("Refresh token invalid", code="TOKEN_INVALID")
    user = db.get(User, payload["sub"])
    if not user or not user.is_active:
        raise Unauthorized("User inactive")
    return _issue(user, response)  # rotates refresh cookie


@router.post("/logout", status_code=204)
def logout(response: Response, _: CurrentUser):
    response.delete_cookie(REFRESH_COOKIE, path="/api/v1/auth")


@router.get("/me", response_model=MeOut)
def me(user: CurrentUser):
    return _me(user)
