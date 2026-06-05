from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, Token, UserLogin
from app.services.auth import AuthService

router = APIRouter()


@router.post("/register", response_model=UserOut)
def register(data: UserCreate, db: Session = Depends(get_db)):
    svc = AuthService(db)
    try:
        return svc.register(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    svc = AuthService(db)
    try:
        token = svc.login(data.username, data.password)
        return Token(access_token=token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
