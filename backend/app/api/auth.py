import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.models import User, UserRole
from app.schemas.auth_schema import UserSignup, TokenResponse, UserOut

router = APIRouter()

@router.post("/auth/signup", response_model=UserOut)
def signup(user: UserSignup, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    if user.role not in [r.value for r in UserRole]:
        raise HTTPException(status_code=400, detail="Invalid role")

    new_user = User(
        id=uuid.uuid4(),
        name=user.name,
        email=user.email,
        phone=user.phone,
        hashed_password=hash_password(user.password),
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserOut(
        id=str(new_user.id),
        name=new_user.name,
        email=new_user.email,
        role=new_user.role.value
    )

@router.post("/auth/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})

    return TokenResponse(
        access_token=access_token,
        role=user.role.value
    )