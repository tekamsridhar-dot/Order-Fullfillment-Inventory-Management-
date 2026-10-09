from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import settings
from app.core.security import (create_access_token,create_refresh_token,hash_password,
                               hash_refresh_token,verify_password)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.services.audit_service import record_audit

def register_user(db: Session,
                  name: str,
                  email: str,
                  password: str,
                  role_id: int) -> User:
    existing_user = db.scalar(select(User).where(User.email == email))
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email already registered")
    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role_id=role_id,
        is_active=True)
    
    record_audit(
    db=db,
    user_id=user.id,
    action="USER_REGISTERED",
    entity="USER",
    entity_id=user.id,
    metadata={
        "message": "User registered successfully"})
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session,
                      email: str,
                      password: str) -> User:
    user = db.scalar(select(User).where(User.email==email))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or password")
    if not verify_password(password,user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="User account is inactive")
    record_audit(
    db=db,
    user_id=user.id,
    action="USER_REGISTERED",
    entity="USER",
    entity_id=user.id,
    metadata={
        "message": "User registered successfully"
    },
)
    return user

def create_token_pair(db: Session,user: User):
    access_token = create_access_token(user_id=user.id,role=user.role.name)
    refresh_token = create_refresh_token()
    refresh_token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(refresh_token),
        expires_at=datetime.now(timezone.utc)+ timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        revoked=False)
    db.add(refresh_token_record)
    db.commit()
    return access_token, refresh_token
  
def rotate_refresh_token(db: Session,refresh_token_value: str):
    token_hash = hash_refresh_token(refresh_token_value)
    token_record =db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash).
                              with_for_update())
    if token_record is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid refresh token")
    # Already used or logged out
    if token_record.revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Refresh token has been revoked")
    # Expired token
    now = datetime.now(timezone.utc)
    if token_record.expires_at <= now:
        token_record.revoked = True
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Refresh token has expired")
    user = db.scalar(select(User).where(User.id == token_record.user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="User account is inactive")
    # Revoke the old refresh token
    token_record.revoked = True
    # Create new tokens
    new_access_token = create_access_token(user_id=user.id,
                                           role=user.role.name)
    new_refresh_token = create_refresh_token()
    new_refresh_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(new_refresh_token),
        expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        revoked=False)
    db.add(new_refresh_record)
    db.commit()
    return new_access_token, new_refresh_token

def revoke_refresh_token(db: Session,refresh_token_value: str):
    token_hash = hash_refresh_token(refresh_token_value)
    token_record = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    if token_record is None:
        return
    token_record.revoked = True
    db.commit()

