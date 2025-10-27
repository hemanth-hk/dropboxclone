from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# User Schemas
class UserCreate(BaseModel):
    """Schema for user registration"""
    username: str
    password: str


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    username: str
    
    class Config:
        from_attributes = True


# Authentication Schemas
class TokenRequest(BaseModel):
    """Schema for authentication request (Basic Auth will be extracted from header)"""
    pass


class TokenResponse(BaseModel):
    """Schema for token response"""
    token: str
    message: str


# File Schemas
class FileInfo(BaseModel):
    """Schema for file metadata"""
    id: int
    filename: str
    size: int
    upload_date: datetime
    
    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    """Schema for paginated file list response"""
    files: list[FileInfo]
    total: int
    page: int
    page_size: int


class FileUploadResponse(BaseModel):
    """Schema for file upload response"""
    id: int
    filename: str
    url: str
    size: int
    message: str


class FileDownloadRequest(BaseModel):
    """Schema for file download request"""
    file_id: int


class FileDeleteResponse(BaseModel):
    """Schema for file delete response"""
    message: str

