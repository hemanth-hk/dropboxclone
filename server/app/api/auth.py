"""Authentication API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.tables import Session as SessionModel
from app.models import UserCreate, UserResponse, LoginRequest, TokenResponse, RefreshRequest
from app.services.user_service import create_user, get_user_by_username
from app.services.auth_service import authenticate_user, store_refresh_token, verify_refresh_token
from app.core.security import hash_password, create_access_token, create_refresh_token
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with hashed password."""
    # Check if user already exists
    existing_user = get_user_by_username(db, user.userName)
    if existing_user:
        logger.warning(f"Registration failed: username already exists - {user.userName}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Hash password and create user
    hashed_pwd = hash_password(user.password)
    db_user = create_user(db, user, hashed_pwd)
    
    return UserResponse.model_validate(db_user)


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT tokens."""
    # Authenticate user
    user = authenticate_user(login_data.userName, login_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create JWT access token
    access_token = create_access_token(user.id)
    
    # Create refresh token
    refresh_token = create_refresh_token(user.id)
    
    # Store refresh token in database
    store_refresh_token(user.id, refresh_token, db)
    
    logger.info(f"User logged in: {login_data.userName}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=900  # 15 minutes
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(refresh_data: RefreshRequest, db: Session = Depends(get_db)):
    """Refresh access token using a valid refresh token."""
    # Verify refresh token
    user_id = verify_refresh_token(refresh_data.refresh_token, db)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Create new JWT access token
    access_token = create_access_token(user_id)
    
    # Create new refresh token
    new_refresh_token = create_refresh_token(user_id)
    
    # Delete old refresh token
    old_session = db.query(SessionModel).filter(SessionModel.token == refresh_data.refresh_token).first()
    if old_session:
        db.delete(old_session)
        db.commit()
    
    # Store new refresh token
    store_refresh_token(user_id, new_refresh_token, db)
    
    logger.info(f"Tokens refreshed for user_id={user_id}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=900  # 15 minutes
    )

