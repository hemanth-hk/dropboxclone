"""User service for user-related operations."""
from sqlalchemy.orm import Session
from typing import Optional

from app.db.tables import User
from app.models.user import UserCreate
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return db.query(User).filter(User.userName == username).first()


def create_user(db: Session, user_data: UserCreate, hashed_password: str) -> User:
    """Create a new user with hashed password."""
    db_user = User(
        displayName=user_data.displayName,
        userName=user_data.userName,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"Created new user: {user_data.userName}")
    return db_user

