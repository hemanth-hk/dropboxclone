"""File service for file-related operations."""
from sqlalchemy.orm import Session
from typing import Optional, List

from app.db.tables import File, UserToFileAssociation
from app.core.logging import get_logger

logger = get_logger(__name__)


def create_file_metadata(
    db: Session,
    fileName: str,
    fileType: str,
    fileSize: int,
    filePath: str
) -> File:
    """Create file metadata in database."""
    db_file = File(
        fileName=fileName,
        fileType=fileType,
        fileSize=fileSize,
        filePath=filePath
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    logger.info(f"Created file metadata: {fileName} (id={db_file.id})")
    return db_file


def get_file_metadata_by_id(db: Session, file_id: int) -> Optional[File]:
    """Get file metadata by ID."""
    return db.query(File).filter(File.id == file_id).first()


def get_user_files_count(db: Session, user_id: int) -> int:
    """Get total count of files for a user."""
    return db.query(UserToFileAssociation).filter(UserToFileAssociation.userId == user_id).count()


def get_user_files(
    db: Session,
    user_id: int,
    page: int = 1,
    page_size: int = 10
) -> List[File]:
    """Get user's files with pagination."""
    offset = (page - 1) * page_size
    return db.query(File).join(
        UserToFileAssociation,
        File.id == UserToFileAssociation.fileId
    ).filter(
        UserToFileAssociation.userId == user_id
    ).offset(offset).limit(page_size).all()


def get_user_file_association(db: Session, user_id: int, file_id: int) -> Optional[UserToFileAssociation]:
    """Get user-file association."""
    return db.query(UserToFileAssociation).filter(
        UserToFileAssociation.userId == user_id,
        UserToFileAssociation.fileId == file_id
    ).first()


def create_user_file_association(db: Session, user_id: int, file_id: int) -> UserToFileAssociation:
    """Create user-file association."""
    association = UserToFileAssociation(
        userId=user_id,
        fileId=file_id
    )
    db.add(association)
    db.commit()
    db.refresh(association)
    logger.info(f"Created user-file association: user_id={user_id}, file_id={file_id}")
    return association


def delete_file_and_association(db: Session, file_id: int) -> bool:
    """Delete file metadata and its association within a transaction."""
    try:
        with db.begin_nested():
            association = db.query(UserToFileAssociation).filter(
                UserToFileAssociation.fileId == file_id
            ).first()
            
            if association:
                db.delete(association)
            
            file_metadata = db.query(File).filter(File.id == file_id).first()
            
            if file_metadata:
                db.delete(file_metadata)
                logger.info(f"Deleted file and association: file_id={file_id}")
                return True
        db.commit()
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete file and association for file_id={file_id}: {e}")
        return False

