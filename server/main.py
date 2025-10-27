from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import HTTPBasic
from fastapi.responses import JSONResponse
import uvicorn
from sqlalchemy.orm import Session
from database import get_db
from schemas import UserCreate, UserResponse, TokenResponse
from auth import authenticate_user, create_session, extract_basic_auth, get_current_user
from crud import create_user, get_user_by_username, get_user_by_id

app = FastAPI()


@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with username and password.
    
    Returns:
        UserResponse: The created user object
    """
    # Check if user already exists
    existing_user = get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user
    db_user = create_user(db, user)
    return UserResponse(id=db_user.id, username=db_user.username)


@app.post("/token", response_model=TokenResponse)
def token(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Authenticate user using Basic Auth and return a session token.
    
    Returns:
        TokenResponse: Session token and message
    """
    # Get authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Extract username and password from Basic Auth
    username, password = extract_basic_auth(auth_header)
    
    # Authenticate user
    user = authenticate_user(username, password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Create session and generate token
    token = create_session(user.id, db)
    
    return TokenResponse(
        token=token,
        message="Authentication successful"
    )


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)