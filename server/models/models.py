from pydantic import BaseModel
from fastapi import Form


class Registration(BaseModel):
    fullname: str = Form(...)
    email: str = Form(...)
    phone: int = Form(...)
    password: str = Form(...)

    class Config:
        orm_mode = True
