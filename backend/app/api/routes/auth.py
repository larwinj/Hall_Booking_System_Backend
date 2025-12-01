from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from app.db.session import get_db
from app.core.config import get_settings
from app.core.security import get_password_hash, verify_password, create_token, decode_token
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.user import ForgotPasswordRequest, UserCreate, UserOut, TokenPair, ModeratorRegistration, LoginRequest

from fastapi.security import OAuth2PasswordRequestForm

from app.models.venue import Venue
from app.api.deps import get_current_user  

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserOut,description="Access by everyone")
async def signup(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = (await db.execute(select(User).where(User.email == payload.email))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=payload.email, hashed_password=get_password_hash(payload.password), role=UserRole.customer)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/register_moderator", response_model=UserOut,description="Access by the moderator users.")
async def register_moderator(payload: ModeratorRegistration, db: AsyncSession = Depends(get_db)):
    existing = (await db.execute(select(User).where(User.email == payload.user.email))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.user.email,
        hashed_password=get_password_hash(payload.user.password),
        role=UserRole.moderator
    )
    db.add(user)
    await db.flush()
    venue = Venue(**payload.venue.model_dump())
    db.add(venue)
    await db.flush()
    user.assigned_venue_id = venue.id
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login", response_model=TokenPair,description="Access by everyone")
async def login(response: Response,form_data: LoginRequest,db: AsyncSession = Depends(get_db),):
    user = (await db.execute(select(User).where(User.email == form_data.username))).scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    settings = get_settings()
    access = create_token(
        subject=user.id,
        secret=settings.JWT_SECRET,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        algorithm=settings.ALGORITHM,
        token_type="access",
        token_version=user.token_version,
        role=user.role.value,
        assigned_venue_id=user.assigned_venue_id,
    )
    refresh = create_token(
        subject=user.id,
        secret=settings.JWT_REFRESH_SECRET,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        algorithm=settings.ALGORITHM,
        token_type="refresh",
        token_version=user.token_version,
    )

    access_max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    refresh_max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600

    response.set_cookie(
        key="access_token",
        value=access,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=access_max_age,
        expires=access_max_age,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=refresh_max_age,
        expires=refresh_max_age,
        path="/auth",
    )
    response.set_cookie(
        key="user_role",
        value=user.role.value,
        httponly=False,
        secure=True,
        samesite="lax",
        max_age=refresh_max_age,
        path="/",
    )

    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    settings = get_settings()
    try:
        payload = decode_token(refresh_token, secret=settings.JWT_REFRESH_SECRET, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        sub = int(payload.get("sub"))
        token_ver = int(payload.get("ver", 0))
        user = (await db.execute(select(User).where(User.id == sub))).scalar_one_or_none()
        if not user or user.token_version != token_ver:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        access = create_token(
            subject=user.id,
            secret=settings.JWT_SECRET,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            algorithm=settings.ALGORITHM,
            token_type="access",
            token_version=user.token_version,
            role=user.role.value,
            assigned_venue_id=user.assigned_venue_id,
        )
        new_refresh = create_token(
            subject=user.id,
            secret=settings.JWT_REFRESH_SECRET,
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            algorithm=settings.ALGORITHM,
            token_type="refresh",
            token_version=user.token_version,
        )
        return TokenPair(access_token=access, refresh_token=new_refresh)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.post("/logout",description="Access by everyone")
async def logout(
    response: Response,
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    user.token_version += 1
    await db.commit()
    
    # Clear all cookies
    response.set_cookie(
        key="access_token",
        value="",
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=0,
        expires=0,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value="",
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=0,
        expires=0,
        path="/auth",
    )
    response.set_cookie(
        key="user_role",
        value="",
        httponly=False,
        secure=True,
        samesite="lax",
        max_age=0,
        expires=0,
        path="/",
    )
    
    return {"success": True, "message": "Logged out successfully"}

@router.post("/forgot-password", description="Access by everyone - Reset user password")
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    # Find user by email
    user = (await db.execute(select(User).where(User.email == payload.email))).scalar_one_or_none()
    
    if not user:
        return {
            "success": True,
            "message": "If the email exists, password has been reset successfully"
        }
    
    # Update user password
    user.hashed_password = get_password_hash(payload.new_password)
    user.token_version += 1  
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Password has been reset successfully"
    }