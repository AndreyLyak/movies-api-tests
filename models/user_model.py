# models/user_model.py
from pydantic import BaseModel, Field
from typing import Optional, List
from enums.roles import Roles


class RegisterUserResponse(BaseModel):
    """Модель ответа при регистрации пользователя"""
    id: str
    email: str
    fullName: str
    verified: bool
    banned: Optional[bool] = None
    roles: List[str]
    createdAt: str = Field(alias="createdAt")
    updatedAt: Optional[str] = Field(None, alias="updatedAt")


class TestUser(BaseModel):
    """Модель для тестовых данных пользователя"""
    email: str
    fullName: str
    password: str
    passwordRepeat: str
    roles: List[Roles] = [Roles.USER]