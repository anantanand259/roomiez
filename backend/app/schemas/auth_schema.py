from pydantic import BaseModel
from typing import Optional

class UserSignup(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    password: str
    role: str  # STUDENT, COLLECTOR, or ADMIN

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str

class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True