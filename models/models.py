from fastapi import Form
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    first_name : str = None
    last_name : str = None

class Contact(BaseModel):
    email: EmailStr
    phone: str = Form(default=None, pattern=r"^0*\d{7,15}$", description="только цифры от 7 до 15 символов")

class Feedback(BaseModel):
    name: str = Form(min_length=2, max_length=50)
    message: str = Form(min_length=10, max_length=500)
    contact: Contact