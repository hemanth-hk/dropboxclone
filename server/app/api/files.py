"""File management API routes."""
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import FileInfo, FileListResponse, FileUploadResponse, FileDeleteResponse
from app.services.file_service import (
    create_file_metadata,
    get_file_metadata_by_id,
    get_user_files_count,
    get_user_files,
    get_user_file_association,
    create_user_file_association,
    delete_file_and_association
)
from app.services.auth_service import get_current_user
from app.db.tables import User
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/files", tags=["Files"])


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a file for the authenticated user."""
    try:
        # Create user-specific directory
        user_dir = settings.uploads_path / str(current_user.id)
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename to avoid collisions
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = user_dir / unique_filename
        
        # Save file to disk
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Get file size and type
        file_size = len(content)
        file_type = file.content_type or "application/octet-stream"
        
        # Create file metadata in database
        db_file = create_file_metadata(
            db=db,
            fileName=file.filename,
            fileType=file_type,
            fileSize=file_size,
            filePath=str(file_path)
        )
        
        # Create user-file association
        create_user_file_association(db, current_user.id, db_file.id)
        
        logger.info(f"File uploaded: {file.filename} by user_id={current_user.id}")
        
        return FileUploadResponse(
            id=db_file.id,
            fileName=db_file.fileName,
            fileType=db_file.fileType,
            fileSize=db_file.fileSize,
            filePath=db_file.filePath,
            message="File uploaded successfully"
        )
    
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )


@router.get("/", response_model=FileListResponse)
def list_files(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Files per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all files for the authenticated user with pagination."""
    # Get total count
    total = get_user_files_count(db, current_user.id)
    
    # Get files for current page
    files = get_user_files(db, current_user.id, page, page_size)
    
    # Convert to FileInfo schema
    file_infos = [FileInfo.model_validate(f) for f in files]
    
    logger.info(f"Listed {len(file_infos)} files for user_id={current_user.id}, page={page}")
    
    return FileListResponse(
        files=file_infos,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{file_id}/download")
def download_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download a file by ID."""
    # Get file metadata
    file_metadata = get_file_metadata_by_id(db, file_id)
    
    if not file_metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check if file belongs to the user
    association = get_user_file_association(db, current_user.id, file_id)
    if not association:
        logger.warning(f"Unauthorized file access attempt: file_id={file_id} by user_id={current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this file"
        )
    
    # Check if file exists on disk
    file_path = Path(file_metadata.filePath)
    if not file_path.exists():
        logger.error(f"File not found on disk: {file_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    logger.info(f"File downloaded: {file_metadata.fileName} by user_id={current_user.id}")
    
    # Return file as response
    return FileResponse(
        path=file_path,
        filename=file_metadata.fileName,
        media_type=file_metadata.fileType
    )


@router.delete("/{file_id}", response_model=FileDeleteResponse)
def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a file by ID."""
    # Get file metadata
    file_metadata = get_file_metadata_by_id(db, file_id)
    
    if not file_metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check if file belongs to the user
    association = get_user_file_association(db, current_user.id, file_id)
    if not association:
        logger.warning(f"Unauthorized file deletion attempt: file_id={file_id} by user_id={current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this file"
        )
    
    # Delete file from disk
    file_path = Path(file_metadata.filePath)
    if file_path.exists():
        try:
            file_path.unlink()
            logger.info(f"Deleted file from disk: {file_path}")
        except Exception as e:
            logger.error(f"Error deleting file from disk: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting file from disk: {str(e)}"
            )
    
    # Delete file metadata and association from database
    success = delete_file_and_association(db, file_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting file from database"
        )
    
    logger.info(f"File deleted: file_id={file_id} by user_id={current_user.id}")
    
    return FileDeleteResponse(message="File deleted successfully")

