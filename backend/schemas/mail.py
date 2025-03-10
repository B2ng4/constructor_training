
from pydantic import BaseModel, EmailStr, Field, validator, field_validator



class mail_send(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")
    subject:str
    body:str

