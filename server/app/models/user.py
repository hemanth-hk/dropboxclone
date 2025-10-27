"""Pydantic models for user-related data."""
from pydantic import BaseModel, Field
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for user registration."""
    displayName: str = Field(..., min_length=1, max_length=100, description="User's display name")
    userName: str = Field(..., min_length=3, max_length=50, description="Unique username")
    password: str = Field(..., min_length=6, description="User password")


class UserResponse(BaseModel):
    """Schema for user response data."""
    id: int
    displayName: str
    userName: str
    created: datetime
    modified: datetime
    
    class Config:
        from_attributes = True

