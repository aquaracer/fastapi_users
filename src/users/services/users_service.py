from dataclasses import dataclass
from typing import Optional

from src.models.user_model import UserDB
from src.users.exceptions.users_exceptions import UserNotFoundError
from src.users.repositories.users_repository import UserRepository
from src.users.schemas.users_schema import UserPatchSchema, UserSchema


@dataclass
class UserService:
    user_repository: UserRepository

    async def get_user_or_404(self, user_id: int) -> UserDB:
        """
        Получение пользователя или вызов UserNotFoundError.
        """

        user: Optional[UserDB] = await self.user_repository.get_user_by_id(
            user_id=user_id)
        if not user:
            raise UserNotFoundError()
        return user

    async def get_user_info(self, user_id: int) -> UserSchema:
        """
        Получение информации о пользователе по ID.
        """

        user: UserDB = await self.get_user_or_404(user_id=user_id)
        return UserSchema.model_validate(user)

    async def patch_user(self, body: UserPatchSchema, user_id: int) -> UserSchema:
        """
        Обновление данных пользователя по ID.
        """
        await self.get_user_or_404(user_id=user_id)
        user: UserDB = await self.user_repository.patch_user(body=body, user_id=user_id)
        return UserSchema.model_validate(user)
