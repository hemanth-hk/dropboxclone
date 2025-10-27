"""SQLAlchemy database table definitions."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


class User(Base):
    """User table for authentication and file ownership."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    displayName = Column(String, nullable=False)
    userName = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    created = Column(DateTime, default=datetime.utcnow, nullable=False)
    modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    file_associations = relationship("UserToFileAssociation", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")


class File(Base):
    """File metadata table."""
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    fileName = Column(String, nullable=False)
    fileType = Column(String, nullable=False)
    fileSize = Column(Integer, nullable=False)
    filePath = Column(String, nullable=False)
    created = Column(DateTime, default=datetime.utcnow, nullable=False)
    modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    file_associations = relationship("UserToFileAssociation", back_populates="file", cascade="all, delete-orphan")


class UserToFileAssociation(Base):
    """Association table between users and files (1:1 relationship)."""
    __tablename__ = "user_to_file_association"
    
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    fileId = Column(Integer, ForeignKey("files.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Relationships
    user = relationship("User", back_populates="file_associations")
    file = relationship("File", back_populates="file_associations")
    
    # Ensure unique user-file association
    __table_args__ = (UniqueConstraint('userId', 'fileId', name='unique_user_file'),)


class Session(Base):
    """Session table for storing refresh tokens."""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expiry = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")

