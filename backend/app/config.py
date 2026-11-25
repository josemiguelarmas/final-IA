from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    APP_NAME: str = "Consultorio Jurídico Mantis AI MVP"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./consultorio_juridico.db"
    
    # AI Engine Configuration (100% Local / Zero Commercial APIs)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    AI_TIMEOUT_SECONDS: float = 8.0
    FORCE_RULE_ENGINE: bool = False  # Set to True to bypass Ollama even if available
    
    # Mantis Bug Tracker Integration
    MANTIS_BASE_URL: Optional[str] = "https://www.icesi.edu.co/consultorio-juridico-app"
    MANTIS_API_TOKEN: Optional[str] = None
    MANTIS_ADAPTER_TYPE: str = "mock"  # "mock" or "http"
    
    # Institution Info
    INSTITUTION_NAME: str = "Universidad Icesi - Consultorio Jurídico"
    DEFAULT_SUPERVISOR_NAME: str = "Marcela Andrea Ríos Salazar"
    DEFAULT_SUPERVISOR_EMAIL: str = "mrios@example.edu.co"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
