from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.config.logger import logger
from src.config.limiter import limiter
from src.users.dependencies.auth_dependency import get_auth_service
from src.users.exceptions.users_exceptions import (
    InvalidTokenPayloadError,
    InvalidTokenTypeError,
    PasswordIsNotCorrectError,
    UserExistsError,
    UserNotFoundError,
)
from src.users.schemas.auth_schema import (
    AccessTokenSchema,
    LoginSchema,
    RefreshTokenSchema,
    TokenPairSchema,
)
from src.users.schemas.users_schema import UserRegisterSchema, UserSchema
from src.users.services.auth_service import AuthService

router = APIRouter()

@router.post("/register", response_model=UserSchema,
             status_code=status.HTTP_201_CREATED)
async def create_user(
        body: UserRegisterSchema,
        auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """Регистрация пользователя"""
    try:
        user = await auth_service.create_user(body=body)
        logger.info(
            "user_registered",
            email=body.email,
            user_id=user.id,
            action="register",
        )
        return user
    except UserExistsError as error:
        logger.warning(
            "user_registration_failed",
            email=body.email,
            reason=error.detail,
            action="register",
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=error.detail
        ) from error


@router.post("/login", response_model=TokenPairSchema)
@limiter.limit("5/minute")
async def login(
        request: Request,
        body: LoginSchema,
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """Логин"""
    try:
        tokens = await auth_service.login(email=body.email, password=body.password)
        logger.info(
            "user_logged_in",
            email=body.email,
            ip=request.client.host if request.client else None,
            action="login",
        )
        return tokens
    except (UserNotFoundError, PasswordIsNotCorrectError) as error:
        logger.warning(
            "user_login_failed",
            email=body.email,
            reason=error.detail,
            ip=request.client.host if request.client else None,
            action="login",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=error.detail
        ) from error


@router.post("/refresh", response_model=AccessTokenSchema)
async def refresh_token(
        body: RefreshTokenSchema,
        auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """Обновление access token по refresh token"""
    try:
        new_token = await auth_service.get_new_access_token(
            refresh_token=body.refresh_token)
        logger.info(
            "access_token_refreshed",
            token=body.refresh_token[:8] + "...",
            action="refresh",
        )
        return new_token
    except (InvalidTokenTypeError, InvalidTokenPayloadError) as error:
        logger.warning(
            "refresh_token_failed",
            token=body.refresh_token[:8] + "...",
            reason=error.detail,
            action="refresh",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=error.detail
        ) from error
