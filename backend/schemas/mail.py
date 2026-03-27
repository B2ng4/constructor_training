from pydantic import BaseModel, EmailStr, Field, field_validator, validator


class mail_send(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")
    subject: str
    body: str
