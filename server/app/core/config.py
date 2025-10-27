"""Application configuration using Pydantic BaseSettings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from .env file with validation."""
    
    # Application
    APP_NAME: str = "Dropbox Clone API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "sqlite:///./dropbox.db"
    
    # File Storage
    UPLOADS_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 100
    
    # Server
    HOST: str = "localhost"
    PORT: int = 8080
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    @property
    def uploads_path(self) -> Path:
        """Get uploads directory as Path object."""
        return Path(self.UPLOADS_DIR)
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance. Loads .env only once."""
    return Settings()


# Singleton instance for easy import
settings = get_settings()

