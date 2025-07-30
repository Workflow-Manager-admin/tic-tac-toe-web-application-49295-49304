"""
Authentication utilities for backend.

Includes:
- User registration and login endpoints
- JWT token creation & verification
- Dependency for authenticated user
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from . import crud, database, models, schemas

from typing import Optional

# Secret key (ensure this is set via environment or securely for production!)
import os
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key")  # Should be set in environment
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24  # 1 day

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ========== Utility Functions ==========

# PUBLIC_INTERFACE
def verify_password(plain_password, hashed_password):
    """Verify provided password against hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

# PUBLIC_INTERFACE
def get_password_hash(password):
    """Hash a password for storage."""
    return pwd_context.hash(password)

# PUBLIC_INTERFACE
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT token with optional expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

# PUBLIC_INTERFACE
def decode_access_token(token: str):
    """Decode JWT and return payload if valid, else None."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

# ========== Auth Dependencies ==========

# PUBLIC_INTERFACE
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db)
) -> models.User:
    """Dependency: get currently authenticated user, raises 401 if invalid."""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials"
        )
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credentials not found in token"
        )
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not exist"
        )
    return user

# ========== Schemas ==========

class TokenResponse(schemas.BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserLogin(schemas.BaseModel):
    username: str
    password: str

# ========== Endpoints ==========

# PUBLIC_INTERFACE
@router.post("/register", response_model=schemas.UserOut, summary="Register new user")
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """Create a user account. Username must be unique."""
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    created_user = crud.create_user(db, user)
    return created_user

# PUBLIC_INTERFACE
@router.post("/login", response_model=TokenResponse, summary="Login and retrieve JWT token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    """
    Authenticate with username & password, returns JWT token for session.
    Uses OAuth2 password flow (expects POST with application/x-www-form-urlencoded).
    """
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    token_data = {"sub": user.username}
    access_token = create_access_token(token_data)
    return TokenResponse(access_token=access_token)

# PUBLIC_INTERFACE
@router.get("/me", response_model=schemas.UserOut, summary="Get current authenticated user")
def auth_me(current_user: models.User = Depends(get_current_user)):
    """Return profile for currently authenticated user."""
    return current_user
