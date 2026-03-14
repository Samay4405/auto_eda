"""
Authentication API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from services.auth_service import (
    AuthService,
    TokenData,
    LoginRequest,
    SignupRequest,
    get_current_user,
    Token,
)
from services.database_manager import db_manager

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup", response_model=Token)
async def signup(request: SignupRequest):
    """
    Register a new user

    - **email**: User email address
    - **password**: User password
    - **username**: Optional username
    - **full_name**: Optional full name
    """
    # Check if user already exists
    try:
        user = await db_manager.get_user_profile(request.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    except:
        pass

    return await AuthService.signup(
        email=request.email,
        password=request.password,
        username=request.username,
        full_name=request.full_name,
    )


@router.post("/login", response_model=Token)
async def login(request: LoginRequest):
    """
    Authenticate user with email and password

    - **email**: User email address
    - **password**: User password
    """
    return await AuthService.login(email=request.email, password=request.password)


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: TokenData = Depends(get_current_user)):
    """Refresh access token"""
    return AuthService.refresh_token(current_user)


@router.get("/me")
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """Get current user information"""
    user = await db_manager.get_user_profile(current_user.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.put("/me")
async def update_current_user(
    current_user: TokenData = Depends(get_current_user),
    full_name: str = None,
    username: str = None,
    avatar_url: str = None,
    organization: str = None,
):
    """Update current user profile"""
    updates = {}
    if full_name:
        updates["full_name"] = full_name
    if username:
        updates["username"] = username
    if avatar_url:
        updates["avatar_url"] = avatar_url
    if organization:
        updates["organization"] = organization

    user = await db_manager.update_user_profile(current_user.user_id, **updates)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update profile"
        )
    return user


@router.post("/logout")
async def logout(current_user: TokenData = Depends(get_current_user)):
    """Logout user (client should discard token)"""
    return {"message": "Successfully logged out"}
