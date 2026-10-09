from fastapi import APIRouter, Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select,func
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.auth import get_current_user,require_admin
from app.core.security import create_access_token,create_refresh_token,hash_refresh_token
from app.core.security import verify_password, hash_password
from app.dependencies import get_db
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models import Role
from app.schemas.auth import (RegisterRequest,LoginRequest,TokenResponse,ChangePasswordRequest,
                              RefreshTokenRequest,LogoutRequest,UserResponse)
from app.schemas.auth import UserResponse
from app.services.auth_service import (register_user,authenticate_user,create_token_pair,
                                       rotate_refresh_token,revoke_refresh_token)

router = APIRouter(prefix="/api/auth",
                   tags=["Authentication"])

from sqlalchemy import select
from fastapi import HTTPException

from app.models import Role


@router.post("/register", response_model=UserResponse)
def register(data: RegisterRequest,
             db: Session = Depends(get_db)):
    role = db.scalar(select(Role).where(func.lower(Role.name) == data.role.lower()))
    if not role:
        raise HTTPException(status_code=404,
                            detail="Role not found")
    user = register_user(
        db=db,
        name=data.name,
        email=data.email,
        password=data.password,
        role_id=role.id)
    return user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    user = authenticate_user(db,form_data.username,form_data.password)
    if not user:
        raise HTTPException(status_code=401,
                            detail="Incorrect email or password")
    access_token = create_access_token(user_id=user.id,role=user.role.name)
    refresh_token = create_refresh_token()
    token_hash = hash_refresh_token(refresh_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    token_record = RefreshToken(user_id=user.id,
                                token_hash=token_hash,
                                expires_at=expires_at,
                                revoked=False)
    db.add(token_record)
    db.commit()
    return {
    "access_token": access_token,
    "refresh_token": refresh_token,
    "token_type": "bearer"}

@router.post("/refresh",response_model=TokenResponse)
def refresh_access_token(data: RefreshTokenRequest,
                         db: Session = Depends(get_db)):
    access_token, refresh_token = rotate_refresh_token(db=db,
                                                       refresh_token_value=data.refresh_token)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer")

@router.post("/logout")
def logout(data:LogoutRequest,
           db:Session=Depends(get_db)):
    revoke_refresh_token(db=db,refresh_token_value=data.refresh_token)
    return {"messege":"Loggod out successfully"}

@router.get("/me",response_model=UserResponse)
def get_users(current_user:User=Depends(get_current_user)):
    return current_user

@router.post("/change-password")
def change_password(data: ChangePasswordRequest,
                    current_user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    if not verify_password( data.current_password,current_user.password_hash):
        raise HTTPException(status_code=400,
                            detail="Current password is incorrect")
    current_user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}

