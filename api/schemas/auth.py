from pydantic import BaseModel

class UserRegisterModel(BaseModel):
    username: str
    email: str
    password: str

class UserLoginModel(BaseModel):
    email: str
    password: str

class PasswordResetModel(BaseModel):
    email: str
