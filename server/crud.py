from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from models import User, FilesMetaData, UserToFilesAssociation, Session as SessionModel
from schemas import UserCreate


# User CRUD Operations
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user"""
    db_user = User(
        username=user.username,
        password=user.password  # Storing as plain text as per requirements
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# File CRUD Operations
def create_file_metadata(
    db: Session,
    filename: str,
    url: str,
    size: int
) -> FilesMetaData:
    """Create file metadata"""
    db_file = FilesMetaData(
        filename=filename,
        url=url,
        size=size
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


def get_file_metadata_by_id(db: Session, file_id: int) -> Optional[FilesMetaData]:
    """Get file metadata by ID"""
    return db.query(FilesMetaData).filter(FilesMetaData.id == file_id).first()


def get_user_files_count(db: Session, user_id: int) -> int:
    """Get total count of files for a user"""
    return db.query(UserToFilesAssociation).filter(UserToFilesAssociation.user_id == user_id).count()


def get_user_files(
    db: Session,
    user_id: int,
    page: int = 1,
    page_size: int = 10
) -> List[FilesMetaData]:
    """Get user's files with pagination"""
    offset = (page - 1) * page_size
    return db.query(FilesMetaData).join(
        UserToFilesAssociation,
        FilesMetaData.id == UserToFilesAssociation.file_id
    ).filter(
        UserToFilesAssociation.user_id == user_id
    ).offset(offset).limit(page_size).all()


def get_user_file_association(db: Session, user_id: int, file_id: int) -> Optional[UserToFilesAssociation]:
    """Get user-file association"""
    return db.query(UserToFilesAssociation).filter(
        UserToFilesAssociation.user_id == user_id,
        UserToFilesAssociation.file_id == file_id
    ).first()


def create_user_file_association(db: Session, user_id: int, file_id: int) -> UserToFilesAssociation:
    """Create user-file association"""
    association = UserToFilesAssociation(
        user_id=user_id,
        file_id=file_id
    )
    db.add(association)
    db.commit()
    db.refresh(association)
    return association


def delete_file_and_association(db: Session, file_id: int) -> bool:
    """Delete file metadata and its association"""
    association = db.query(UserToFilesAssociation).filter(
        UserToFilesAssociation.file_id == file_id
    ).first()
    
    if association:
        db.delete(association)
    
    file_metadata = db.query(FilesMetaData).filter(FilesMetaData.id == file_id).first()
    
    if file_metadata:
        db.delete(file_metadata)
        db.commit()
        return True
    
    db.commit()
    return False

