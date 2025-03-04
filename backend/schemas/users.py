from dataclasses import field

from fastapi import Form
from pydantic import BaseModel, EmailStr, Field, validator, field_validator
import re



class User(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")
    phone_number: str = Field(..., description="Номер телефона в международном формате, начинающийся с '+'")
    first_name: str = Field(..., min_length=3, max_length=50, description="Имя, от 3 до 50 символов")
    last_name: str = Field(..., min_length=3, max_length=50, description="Фамилия, от 3 до 50 символов")
    is_admin: bool = False

    class Config:
        from_attributes = True  # Заменяем orm_mode на from_attributes


class UserRegister(User):
    password: str = Field(..., min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")


    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        if not re.match(r'^\+\d{5,15}$', value):
            raise ValueError('Номер телефона должен начинаться с "+" и содержать от 5 до 15 цифр')
        return value



class UserLogin(BaseModel):
    username: EmailStr = Form(...),
    password: str = Form(...)


