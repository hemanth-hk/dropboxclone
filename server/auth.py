import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from database import get_db
from models import User, Session as SessionModel
from crud import get_user_by_username


# Token expiry time (7 days)
TOKEN_EXPIRY_HOURS = 168

# HTTP Bearer Security scheme
security = HTTPBearer(auto_error=False)


def generate_token() -> str:
    """
    Generate a unique UUID-based session token.
    
    Returns:
        str: A unique token string
    """
    return str(uuid.uuid4())


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if the plain password matches the hashed password.
    Since we're storing plain text, we just compare directly.
    
    Args:
        plain_password: The password to verify
        hashed_password: The stored password (plain text in our case)
    
    Returns:
        bool: True if passwords match
    """
    return plain_password == hashed_password


def authenticate_user(username: str, password: str, db: Session) -> Optional[User]:
    """
    Authenticate a user with username and password.
    
    Args:
        username: The username
        password: The password
        db: Database session
    
    Returns:
        User object if authentication successful, None otherwise
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def create_session(user_id: int, db: Session) -> str:
    """
    Create a new session for the user and return the token.
    
    Args:
        user_id: The user ID
        db: Database session
    
    Returns:
        str: The session token
    """
    # Generate new token
    token = generate_token()
    
    # Calculate expiry time
    expiry = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)
    
    # Create session record
    session = SessionModel(
        token=token,
        user_id=user_id,
        expiry=expiry
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return token


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency function to get the current authenticated user from token.
    
    Args:
        credentials: HTTP Bearer credentials containing the token
        db: Database session
    
    Returns:
        User: The authenticated user
    
    Raises:
        HTTPException: If token is invalid, expired, or missing
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Query session from database
    db_session = db.query(SessionModel).filter(SessionModel.token == token).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if token has expired
    if datetime.utcnow() > db_session.expiry:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from session
    user = db.query(User).filter(User.id == db_session.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def extract_basic_auth(auth_header: str) -> tuple[str, str]:
    """
    Extract username and password from Basic Auth header.
    
    Args:
        auth_header: The Authorization header value (e.g., "Basic base64credentials")
    
    Returns:
        tuple: (username, password)
    
    Raises:
        HTTPException: If the auth header is invalid
    """
    try:
        import base64
        
        # Remove "Basic " prefix
        if not auth_header.startswith("Basic "):
            raise ValueError("Invalid auth scheme")
        
        # Decode base64
        encoded = auth_header.split(" ")[1]
        decoded = base64.b64decode(encoded).decode("utf-8")
        
        # Split username and password
        username, password = decoded.split(":", 1)
        return username, password
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication header: {str(e)}",
            headers={"WWW-Authenticate": "Basic"},
        )

