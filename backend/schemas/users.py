from dataclasses import field
from enum import Enum

from fastapi import Form
from pydantic import BaseModel, EmailStr, Field, validator, field_validator
import re





class User(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")
    first_name: str = Field(
        ..., min_length=3, max_length=50, description="Имя, от 3 до 50 символов"
    )
    last_name: str = Field(
        ..., min_length=3, max_length=50, description="Фамилия, от 3 до 50 символов"
    )

    class Config:
        from_attributes = True


class UserRegister(User):
    password: str = Field(
        ..., min_length=5, max_length=100, description="Пароль, от 5 до 100 знаков"
    )


class UserLogin(BaseModel):
    username: EmailStr
    password: str
