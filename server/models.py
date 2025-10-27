from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    """Users table"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    
    # Relationships
    file_associations = relationship("UserToFilesAssociation", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")


class FilesMetaData(Base):
    """FilesMetaData table"""
    __tablename__ = "files_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    url = Column(String, nullable=False)  # Local file path
    size = Column(Integer, nullable=False)  # File size in bytes
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    file_associations = relationship("UserToFilesAssociation", back_populates="file", cascade="all, delete-orphan")


class UserToFilesAssociation(Base):
    """UserToFilesAssociation table - 1:1 relationship between users and files"""
    __tablename__ = "user_to_files_association"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_id = Column(Integer, ForeignKey("files_metadata.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Relationships
    user = relationship("User", back_populates="file_associations")
    file = relationship("FilesMetaData", back_populates="file_associations")
    
    # Ensure unique user-file association
    __table_args__ = (UniqueConstraint('user_id', 'file_id', name='unique_user_file'),)


class Session(Base):
    """Sessions table - stores authentication tokens"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expiry = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")

