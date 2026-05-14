from pydantic import BaseModel, ConfigDict, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)

class LoginData(BaseModel):
    email: EmailStr
    password: str