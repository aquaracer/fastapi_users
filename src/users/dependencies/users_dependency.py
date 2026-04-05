from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import get_db_session
from src.users.repositories.users_repository import UserRepository
from src.users.services.users_service import UserService


async def get_user_repository(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserRepository:
    return UserRepository(db_session=db_session)


async def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(user_repository=user_repository)