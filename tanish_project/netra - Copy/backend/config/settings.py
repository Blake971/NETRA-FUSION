from dotenv import load_dotenv
import os
from typing import Optional

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        # API Keys
        self.gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
        
        # Database
        self.database_url: str = os.getenv("DATABASE_URL", "sqlite:///database/netra.db")
        
        # CORS
        self.frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        # Environment
        self.environment: str = os.getenv("ENVIRONMENT", "development")
        self.debug: bool = os.getenv("DEBUG", "True").lower() == "true"


settings = Settings()
