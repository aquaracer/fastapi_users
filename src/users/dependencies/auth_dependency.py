from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.config.logger import logger
from src.config.project_config import Settings
from src.users.dependencies.users_dependency import get_user_repository
from src.users.exceptions.users_exceptions import (
    TokenExpiredError,
    TokenIsNotCorrectError,
)
from src.users.repositories.users_repository import UserRepository
from src.users.services.auth_service import AuthService


@lru_cache
def get_settings() -> Settings:
    return Settings()


async def get_auth_service(
        user_repository: Annotated[UserRepository, Depends(get_user_repository)],
        settings: Annotated[Settings, Depends(get_settings)],
) -> AuthService:
    return AuthService(
        settings=settings,
        user_repository=user_repository,
    )


bearer_scheme = HTTPBearer()


async def get_user_id(
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        token: Annotated[HTTPAuthorizationCredentials, Security(bearer_scheme)],
) -> int:
    try:
        return auth_service.get_user_id_from_access_token(token.credentials)

    except (TokenExpiredError, TokenIsNotCorrectError) as error:
        logger.warning(
            "access_token_invalid",
            reason=error.detail,
            action="get_user_id",
            token_snippet=token.credentials[:8] + "...",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error.detail,
        ) from error
