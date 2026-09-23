from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.security import decode_access_token
from app.models.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user

def require_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role.value != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Requires {required_role} role")
        return current_user
    return role_checker