"""Pydantic models for authentication."""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Schema for login request."""
    userName: str = Field(..., min_length=3, description="Username")
    password: str = Field(..., min_length=6, description="Password")


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="Refresh token for getting new access tokens")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(default=900, description="Access token expiry in seconds")


class RefreshRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str = Field(..., min_length=1, description="Refresh token")

