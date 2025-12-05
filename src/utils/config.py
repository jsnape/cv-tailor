import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    # AI Model Configuration
    github_token: str
    openai_api_key: str = ""
    default_model_id: str = "gpt-4.1-mini"
    
    # Database Configuration
    database_url: str = "sqlite+aiosqlite:///./cv_tailor.db"
    
    # Security Settings
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    # Application Settings
    debug: bool = False
    app_name: str = "CV Tailor Agent"
    version: str = "1.0.0"
    
    # CORS Settings
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # File Storage
    upload_max_size: int = 10485760  # 10MB
    output_directory: str = "./outputs"
    temp_directory: str = "./temp"
    
    # Rate Limiting
    rate_limit_per_minute: int = 60

    @validator('cors_origins', pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return []

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure output directories exist
os.makedirs(settings.output_directory, exist_ok=True)
os.makedirs(settings.temp_directory, exist_ok=True)