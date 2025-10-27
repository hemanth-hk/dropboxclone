"""Pydantic models for file-related data."""
from pydantic import BaseModel, Field
from datetime import datetime


class FileInfo(BaseModel):
    """Schema for file metadata."""
    id: int
    fileName: str
    fileType: str
    fileSize: int = Field(..., description="File size in bytes")
    created: datetime
    
    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    """Schema for paginated file list response."""
    files: list[FileInfo]
    total: int = Field(..., description="Total number of files")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Number of files per page")


class FileUploadResponse(BaseModel):
    """Schema for file upload response."""
    id: int
    fileName: str
    fileType: str
    fileSize: int
    filePath: str
    message: str


class FileDeleteResponse(BaseModel):
    """Schema for file delete response."""
    message: str

