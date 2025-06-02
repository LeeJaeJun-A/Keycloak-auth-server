from pydantic import BaseModel, EmailStr


class EmailRequest(BaseModel):
    email: EmailStr


class CodeVerifyRequest(BaseModel):
    email: EmailStr
    code: str


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
