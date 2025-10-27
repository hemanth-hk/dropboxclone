"""Authentication service for login and token management."""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.tables import User, Session as SessionModel
from app.db.database import get_db
from app.core.security import verify_password, verify_access_token
from app.core.config import settings
from app.core.logging import get_logger
from app.services.user_service import get_user_by_username

logger = get_logger(__name__)

# HTTP Bearer Security scheme
security = HTTPBearer(auto_error=False)


def authenticate_user(username: str, password: str, db: Session) -> Optional[User]:
    """Authenticate a user with username and password."""
    user = get_user_by_username(db, username)
    if not user:
        logger.warning(f"Authentication failed: user not found - {username}")
        return None
    if not verify_password(password, user.password):
        logger.warning(f"Authentication failed: invalid password - {username}")
        return None
    logger.info(f"User authenticated successfully: {username}")
    return user


def store_refresh_token(user_id: int, refresh_token: str, db: Session) -> None:
    """Store a refresh token in the database."""
    expiry = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    session = SessionModel(
        token=refresh_token,
        user_id=user_id,
        expiry=expiry
    )
    
    db.add(session)
    db.commit()
    logger.info(f"Stored refresh token for user_id={user_id}")


def verify_refresh_token(refresh_token: str, db: Session) -> Optional[int]:
    """Verify a refresh token and return the user ID."""
    db_session = db.query(SessionModel).filter(SessionModel.token == refresh_token).first()
    
    if not db_session:
        logger.warning("Refresh token not found")
        return None
    
    # Check if token has expired
    if datetime.utcnow() > db_session.expiry:
        logger.warning("Refresh token expired")
        db.delete(db_session)
        db.commit()
        return None
    
    logger.info(f"Refresh token verified for user_id={db_session.user_id}")
    return db_session.user_id


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> User:
    """FastAPI dependency to get the current authenticated user from JWT token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Verify JWT token
    user_id = verify_access_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

