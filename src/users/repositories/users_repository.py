from dataclasses import dataclass

from passlib.context import CryptContext
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user_model import UserDB, UserRole
from src.users.schemas.users_schema import UserPatchSchema, UserRegisterSchema

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass
class UserRepository:
    db_session: AsyncSession

    async def get_user_by_email(self, email: str) -> UserDB | None:
        """
        Получение данных о Пользователе по email.
        """

        query = select(UserDB).where(UserDB.email == email, UserDB.is_active)
        async with self.db_session as session:
            return (await session.execute(query)).scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> UserDB | None:
        """
        Получение данных о Пользователе по id
        """

        query = select(UserDB).where(UserDB.id == user_id, UserDB.is_active)
        async with self.db_session as session:
            return (await session.execute(query)).scalar_one_or_none()

    async def create_user(self, body: UserRegisterSchema) -> int:
        """
        Создание Пользователя.
        """

        password_hash = pwd_context.hash(body.password)
        query = (
            insert(UserDB)
            .values(
                email=body.email,
                password_hash=password_hash,
                full_name=body.full_name,
                phone=body.phone,
                role=UserRole.FREE_USER,
                is_active=True,
            )
            .returning(UserDB.id)
        )

        async with self.db_session as session:
            user_id: int = (await session.execute(query)).scalar_one_or_none()
            await session.commit()
        return user_id

    async def patch_user(self, body: UserPatchSchema, user_id: int) -> UserDB:
        """
        Частичное изменение данных Пользователя.
        """

        updates = {k: v for k, v in body.model_dump(exclude_unset=True).items() if
                   v is not None}
        if not updates:
            return await self.get_user_by_id(user_id=user_id)

        async with self.db_session as session:
            query = (
                update(UserDB)
                .where(UserDB.id == user_id, UserDB.is_active)
                .values(**updates)
                .returning(UserDB)
            )
            result = await session.execute(query)
            await session.commit()
            return result.scalar_one_or_none()
