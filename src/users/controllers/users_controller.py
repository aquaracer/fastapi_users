from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.config.logger import logger
from src.users.dependencies.auth_dependency import get_user_id
from src.users.dependencies.users_dependency import get_user_service
from src.users.exceptions.users_exceptions import UserNotFoundError
from src.users.schemas.users_schema import UserPatchSchema, UserSchema
from src.users.services.users_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def get_current_user(
        user_service: Annotated[UserService, Depends(get_user_service)],
        user_id: Annotated[int, Depends(get_user_id)]
):
    """Информация о пользователе"""
    try:
        user = await user_service.get_user_info(user_id=user_id)
        logger.info(
            "get_current_user_success",
            user_id=user_id,
            action="get_current_user",
        )
        return user
    except UserNotFoundError as error:
        logger.warning(
            "get_current_user_failed",
            user_id=user_id,
            reason=error.detail,
            action="get_current_user",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error.detail
        ) from error


@router.patch("/me", response_model=UserSchema)
async def patch_user(
        body: UserPatchSchema,
        user_service: Annotated[UserService, Depends(get_user_service)],
        user_id: Annotated[int, Depends(get_user_id)]
):
    """Изменения данных в профиле пользователя"""
    try:
        updated_user = await user_service.patch_user(body=body, user_id=user_id)
        logger.info(
            "patch_user_success",
            user_id=user_id,
            updated_fields=list(body.model_dump(exclude_unset=True).keys()),
            action="patch_user",
        )
        return updated_user
    except UserNotFoundError as error:
        logger.warning(
            "patch_user_failed",
            user_id=user_id,
            reason=error.detail,
            action="patch_user",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error.detail
        ) from error
