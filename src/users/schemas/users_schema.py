import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class BaseSchema(BaseModel):
    """
    Базовая схема Pydantic с конфигурацией для автоматического создания из атрибутов.
    """
    model_config = ConfigDict(from_attributes=True)


class UserBaseSchema(BaseModel):
    """
    Базовая схема пользователя с email, именем и телефоном.
    """
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def _validate_phone(cls, v):
        """
        Валидация телефона: должен начинаться с '+' и содержать только цифры.
        """
        return validate_phone(v)


def validate_password(value: str) -> str:
    """
    Проверяет пароль: минимум 8 символов и наличие букв.
    """
    if len(value) < 8:
        raise ValueError("Password must be at least 8 characters")
    if value.isdigit():
        raise ValueError("Password must contain letters")
    return value


def validate_phone(value: Optional[str]) -> Optional[str]:
    """
    Проверяет телефон: должен начинаться с '+' и содержать только цифры.
    """
    if value is None:
        return value
    if not re.fullmatch(r"\+\d+", value):
        raise ValueError("Phone must start with '+' and contain only digits")
    return value


class UserSchema(UserBaseSchema, BaseSchema):
    """
    Схема пользователя для чтения данных с ID, ролью и датами создания/обновления.
    """
    id: int
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserRegisterSchema(UserBaseSchema):
    """
    Схема регистрации пользователя с валидацией пароля.
    """
    password: str

    @field_validator("password")
    @classmethod
    def _validate_password(cls, v):
        """Валидация пароля при регистрации."""
        return validate_password(v)


class UserPatchSchema(BaseModel):
    """
    Схема для частичного обновления данных пользователя.
    """
    full_name: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def _validate_phone(cls, v):
        """
        Валидация телефона при обновлении данных.
        """
        return validate_phone(v)
