import datetime
from dataclasses import dataclass
from typing import Optional

from jose import JWTError, jwt
from pydantic import BaseModel

from src.config.project_config import Settings
from src.models.user_model import UserDB
from src.users.exceptions.users_exceptions import (
    InvalidTokenPayloadError,
    InvalidTokenTypeError,
    PasswordIsNotCorrectError,
    TokenExpiredError,
    TokenIsNotCorrectError,
    UserExistsError,
    UserNotFoundError,
)
from src.users.repositories.users_repository import UserRepository, pwd_context
from src.users.schemas.auth_schema import AccessTokenSchema, TokenPairSchema
from src.users.schemas.users_schema import UserRegisterSchema, UserSchema


class JWTPayload(BaseModel):
    sub: str
    iat: datetime.datetime
    exp: datetime.datetime
    role: Optional[str] = None
    type: str


@dataclass
class AuthService:
    user_repository: UserRepository
    settings: Settings

    async def create_user(self, body: UserRegisterSchema) -> UserSchema:
        """
        Создание нового пользователя.
        """

        user: Optional[UserDB] = await self.user_repository.get_user_by_email(
            email=body.email)

        if user:
            raise UserExistsError()

        user_id = await self.user_repository.create_user(body=body)
        user = await self.user_repository.get_user_by_id(user_id=user_id)
        return UserSchema.model_validate(user)

    async def login(self, email: str, password: str) -> TokenPairSchema:
        """
        Авторизация пользователя по почте и паролю. Возвращает пару токенов (access и
         refresh).
        """

        user = await self.user_repository.get_user_by_email(email=email)
        self._validate_auth_user(user=user, password=password)
        access_token = self.create_access_token(user=user)
        refresh_token = self.create_refresh_token(user_id=str(user.id))
        return TokenPairSchema(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    def _validate_auth_user(user: Optional[UserDB], password: str) -> None:
        """
        Проверка существование пользователя и корректности пароля.
        """

        if not user:
            raise UserNotFoundError()

        if not pwd_context.verify(password, user.password_hash):
            raise PasswordIsNotCorrectError()

    def create_access_token(self, user: UserDB) -> str:
        """
        Создание JWT access token.
        """

        now = datetime.datetime.now(datetime.timezone.utc)
        expire = self._get_expiry_timestamp(
            minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user.id),
            "iat": now,
            "exp": expire,
            "role": user.role,
            "type": "access"
        }
        token = self._encode_jwt(payload=payload)
        return token

    def create_refresh_token(self, user_id: str) -> str:
        """
        Создание JWT refresh token.
        """

        now = datetime.datetime.now(datetime.timezone.utc)
        expire = self._get_expiry_timestamp(
            days=self.settings.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": user_id,
            "iat": now,
            "exp": expire,
            "type": "refresh"
        }
        token = self._encode_jwt(payload=payload)
        return token

    async def get_new_access_token(self, refresh_token: str) -> AccessTokenSchema:
        """
        Получение нового JWT access token по refresh token.
        """

        payload_dict = self._decode_token(refresh_token)
        payload = JWTPayload(**payload_dict)

        if payload.type != "refresh":
            raise InvalidTokenTypeError()

        if not payload.sub:
            raise InvalidTokenPayloadError()

        user = await self.user_repository.get_user_by_id(user_id=int(payload.sub))
        if not user or not user.is_active:
            raise InvalidTokenPayloadError()

        access_token = self.create_access_token(user=user)
        return AccessTokenSchema(access_token=access_token)

    def get_user_id_from_access_token(self, access_token: str) -> int:
        """
        Получение user_id из access_token.
        """

        payload_dict = self._decode_token(access_token)
        payload = JWTPayload(**payload_dict)
        now = datetime.datetime.now(datetime.timezone.utc)
        if payload.exp < now:
            raise TokenExpiredError()

        return int(payload.sub)

    def _get_expiry_timestamp(self, minutes: int = 0,
                              days: int = 0) -> datetime.datetime:
        """
        Вычислиние метки времени истечения через заданные минуты или дни.
        """

        now = datetime.datetime.now(datetime.timezone.utc)
        return now + datetime.timedelta(minutes=minutes, days=days)

    def _decode_token(self, token: str) -> dict:
        """
        Декодировка JWT токена. Возвращает payload.
        """

        try:
            return jwt.decode(token, self.settings.JWT_SECRET_KEY,
                              algorithms=[self.settings.JWT_ENCODE_ALGORITHM])
        except JWTError as e:
            raise TokenIsNotCorrectError() from e

    def _encode_jwt(self, payload: dict) -> str:
        """
        Единый метод для кодирования JWT
        """

        return jwt.encode(
            payload,
            self.settings.JWT_SECRET_KEY,
            algorithm=self.settings.JWT_ENCODE_ALGORITHM
        )
