"""
Authentication module for Automated EDA
Handles JWT tokens, user authentication, and authorization with Supabase
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

security = HTTPBearer()


class TokenData(BaseModel):
    user_id: str
    email: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str


class LoginRequest(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    email: str
    password: str
    username: Optional[str] = None
    full_name: Optional[str] = None


class PasswordResetRequest(BaseModel):
    email: str


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


def create_access_token(
    user_id: str, email: Optional[str] = None, expires_delta: Optional[timedelta] = None
):
    """Create a JWT access token"""
    if expires_delta is None:
        expires_delta = timedelta(hours=JWT_EXPIRATION_HOURS)

    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "user_id": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """Verify and decode JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("user_id")
        email: str = payload.get("email")

        if user_id is None:
            raise credentials_exception

        return TokenData(user_id=user_id, email=email)
    except JWTError:
        raise credentials_exception


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
) -> TokenData:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    return verify_token(token)


async def get_optional_user(
    credentials: Optional[HTTPAuthCredentials] = Depends(security),
) -> Optional[TokenData]:
    """Dependency to optionally get authenticated user (for public endpoints)"""
    if not credentials:
        return None

    try:
        token = credentials.credentials
        return verify_token(token)
    except HTTPException:
        return None


class AuthService:
    """Handles authentication operations"""

    @staticmethod
    async def login(email: str, password: str):
        """Authenticate user with email and password"""
        # This should be integrated with your authentication provider
        # For now, returning a placeholder implementation
        # In production, use Supabase Auth or similar service
        from services.database_manager import db_manager

        try:
            # Verify credentials (implement with your auth provider)
            # This is a placeholder - implement actual authentication
            user_id = "user_id"  # Get from auth provider

            # Create JWT token
            access_token = create_access_token(user_id=user_id, email=email)

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": user_id,
            }
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

    @staticmethod
    async def signup(
        email: str,
        password: str,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
    ):
        """Register a new user"""
        from services.database_manager import db_manager

        try:
            # Create user with auth provider (implement with Supabase)
            # This is a placeholder
            user_id = "user_id"  # Get from auth provider

            # Create user profile in database
            await db_manager.create_user_profile(
                user_id=user_id, email=email, username=username, full_name=full_name
            )

            # Create JWT token
            access_token = create_access_token(user_id=user_id, email=email)

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": user_id,
            }
        except Exception as e:
            logger.error(f"Signup error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User registration failed",
            )

    @staticmethod
    def refresh_token(current_user: TokenData) -> Token:
        """Refresh user's access token"""
        new_token = create_access_token(
            user_id=current_user.user_id, email=current_user.email
        )
        return Token(
            access_token=new_token, token_type="bearer", user_id=current_user.user_id
        )
