from pydantic import BaseModel, EmailStr


class LoginSchema(BaseModel):
    """Данные для входа пользователя"""
    email: EmailStr
    password: str


class TokenPairSchema(BaseModel):
    """Пара токенов: access и refresh"""
    access_token: str
    refresh_token: str


class AccessTokenSchema(BaseModel):
    """Access token"""
    access_token: str


class RefreshTokenSchema(BaseModel):
    """Refresh token"""
    refresh_token: str
