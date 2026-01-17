from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.api.v1.deps import DbSession, CurrentUser
from app.schemas import UserCreate, UserUpdate, UserResponse, TokenResponse
from app.services import AuthService
from app.core.exceptions import ConflictError, UnauthorizedError

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: DbSession):
    """Register a new user."""
    auth_service = AuthService(db)
    
    # Check if email exists
    if await auth_service.get_user_by_email(user_data.email):
        raise ConflictError("Email already registered")
    
    # Check if username exists
    if await auth_service.get_user_by_username(user_data.username):
        raise ConflictError("Username already taken")
    
    # Create user
    user = await auth_service.create_user(user_data)
    token = auth_service.create_user_token(user)
    
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
):
    """Login with username and password."""
    auth_service = AuthService(db)
    
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise UnauthorizedError("Invalid username or password")
    
    token = auth_service.create_user_token(user)
    
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: CurrentUser):
    """Get current user's profile."""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    """Update current user's profile."""
    if user_update.email:
        auth_service = AuthService(db)
        existing = await auth_service.get_user_by_email(user_update.email)
        if existing and existing.id != current_user.id:
            raise ConflictError("Email already in use")
        current_user.email = user_update.email
    
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    await db.flush()
    await db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)
