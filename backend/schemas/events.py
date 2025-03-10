from pydantic import BaseModel, EmailStr, Field, validator, field_validator



class event_create(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")
    subject:str
    body:str