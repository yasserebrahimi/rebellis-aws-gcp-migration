from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies import get_db, get_current_user
from src.api.schemas.auth import UserCreate, UserLogin, TokenResponse, UserResponse
from src.services.auth_service import AuthService
from src.models.user import User

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    if await svc.get_user_by_email(user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await svc.create_user(user_data)
    return user

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    user = await svc.authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = await svc.create_access_token(user)
    return TokenResponse(access_token=token, token_type="bearer")

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/logout")
async def logout():
    return {"message": "Successfully logged out"}
